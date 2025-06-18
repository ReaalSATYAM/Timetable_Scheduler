import java.io.*;
import java.util.List;
import java.util.ArrayList;
import javafx.application.Application;
import javafx.beans.property.SimpleStringProperty;
import javafx.stage.*;
import javafx.scene.*;
import javafx.scene.control.*;
import javafx.scene.control.Alert.AlertType;
import javafx.scene.layout.*;
import javafx.scene.text.Text;

public class TimetableGUI extends Application {

    private StackPane mainContent = new StackPane();
    private Scene scene;
    private TextField sectionField = new TextField();
    private File selectedExcelFile = null;
    private String[] sectionList = new String[0];

    @Override
    public void start(Stage primaryStage) {
        VBox sidebar = createSidebar();

        mainContent.getChildren().clear();
        HBox root = new HBox(sidebar, mainContent);
        scene = new Scene(root, 1000, 700);
        scene.getStylesheets().add(getClass().getResource("style.css").toExternalForm());

        primaryStage.setTitle("JavaFX Timetable Dashboard");
        primaryStage.setScene(scene);
        primaryStage.show();
    }

    private VBox createSidebar() {
        VBox sidebar = new VBox(15);
        sidebar.setPrefWidth(290);
        sidebar.getStyleClass().add("sidebar");

        Label title = new Label("Dashboard");
        title.getStyleClass().add("label-title");

        Button adminBtn = new Button("Admin Dashboard");
        Button generateBtn = new Button("Show Timetable");
        Button vacantBtn = new Button("Vacant Classes");

        adminBtn.getStyleClass().add("sidebar-button");
        generateBtn.getStyleClass().addAll("sidebar-button");
        vacantBtn.getStyleClass().add("sidebar-button");

        adminBtn.setOnAction(e -> {
            setActiveButton(adminBtn);
            showLoginScreen("Admin");
        });

        generateBtn.setOnAction(e -> {
            setActiveButton(generateBtn);
            showTimetableTable();
        });

        vacantBtn.setOnAction(e -> {
            setActiveButton(vacantBtn);
            showVacantClassTable();
        });


        sidebar.getChildren().addAll(title, adminBtn, generateBtn, vacantBtn);
        return sidebar;
    }

    private void setActiveButton(Button selectedButton) {
        Scene scene = selectedButton.getScene();
        if (scene == null) return;

        Parent root = scene.getRoot();
        for (Node node : root.lookupAll(".sidebar-button")) {
            if (node instanceof Button button) {
                button.getStyleClass().remove("active");
            }
        }
        selectedButton.getStyleClass().add("active");
    }

    private void showAdminDashboard() {
        mainContent.getChildren().clear();

        Label adminContent = new Label("Admin Dashboard: Manage Timetable");
        adminContent.getStyleClass().add("label-title");

        Label instructions = new Label("1. Download the sample Excel file.\n2. Fill in subject, code, faculty, and sections.\n3. Upload it and enter sections.\n4. Click Generate.");
        instructions.setWrapText(true);

        Button downloadDemoButton = new Button("Download Sample Excel");
        downloadDemoButton.getStyleClass().add("Nbutton");
        downloadDemoButton.setOnAction(e -> {
            try {
                java.nio.file.Path source = java.nio.file.Paths.get("demo.xlsx");
                java.nio.file.Path target = java.nio.file.Paths.get(System.getProperty("user.home"), "Downloads", "demo.xlsx");
                java.nio.file.Files.copy(source, target, java.nio.file.StandardCopyOption.REPLACE_EXISTING);
                showInfoMessage("✅ Demo file saved to Downloads.");
            } catch (Exception ex) {
                ex.printStackTrace();
                showErrorMessage("Failed to copy demo.xlsx: " + ex.getMessage());
            }
        });

        Label sectionLabel = new Label("Enter Sections (comma-separated):");
        sectionField.setPromptText("e.g., K1,K2,L1,L2");

        Label uploadLabel = new Label("Upload Modified Excel:");
        TextField filePathField = new TextField();
        filePathField.setPromptText("No file selected");
        filePathField.setEditable(false);

        Button browseButton = new Button("Browse");
        browseButton.getStyleClass().add("Nbutton");
        final File[] selectedFile = new File[1];
        browseButton.setOnAction(e -> {
            FileChooser fileChooser = new FileChooser();
            fileChooser.setTitle("Select Excel File");
            fileChooser.getExtensionFilters().add(new FileChooser.ExtensionFilter("Excel Files", "*.xlsx"));
            File file = fileChooser.showOpenDialog(null);
            if (file != null) {
                selectedFile[0] = file;
                filePathField.setText(file.getAbsolutePath());
                selectedExcelFile = file;
            }
        });

        HBox fileUploadBox = new HBox(10, filePathField, browseButton);

        Button generateBtn = new Button("Generate Timetable");
        generateBtn.getStyleClass().add("Nbutton");
        generateBtn.setOnAction(e -> {
            if (selectedExcelFile == null) {
                showErrorMessage("Please select an Excel file first.");
                return;
            }
            String sectionText = sectionField.getText().trim();
            if (sectionText.isEmpty()) {
                showErrorMessage("Please enter the list of sections.");
                return;
            }

            sectionList = sectionText.split("\\s*,\\s*");

            try {
                ProcessBuilder pb = new ProcessBuilder("python", "generate_timetable.py", selectedExcelFile.getAbsolutePath(), sectionText);
                pb.redirectErrorStream(true);

                Process process = pb.start();
                BufferedReader reader = new BufferedReader(new InputStreamReader(process.getInputStream()));
                StringBuilder output = new StringBuilder();
                String line;
                while ((line = reader.readLine()) != null) {
                    output.append(line).append("\n");
                }

                int exitCode = process.waitFor();
                if (exitCode == 0) {
                    showInfoMessage("✅ Timetable generated!");
                } else {
                    showErrorMessage("❌ Python Error:\n" + output);
                }
            } catch (Exception ex) {
                showErrorMessage("❌ Error running script: " + ex.getMessage());
            }
        });

        VBox adminLayout = new VBox(20, adminContent, instructions, downloadDemoButton,
                sectionLabel, sectionField, uploadLabel, fileUploadBox, generateBtn);
        adminLayout.setStyle("-fx-padding: 40px;");
        mainContent.getChildren().add(adminLayout);
    }

    private void showVacantClassTable() {
        mainContent.getChildren().clear();

        File file = new File("vacant_classes_all_sections.csv");
        if (!file.exists()) {
            showErrorMessage("Vacant class report not found. Please generate timetable first.");
            return;
        }

        TableView<String[]> tableView = new TableView<>();

        try (BufferedReader reader = new BufferedReader(new FileReader(file))) {
            String line;
            boolean isHeader = true;

            while ((line = reader.readLine()) != null) {
                String[] row = parseCSVLine(line);

                if (isHeader) {
                    for (int i = 0; i < row.length; i++) {
                        final int colIndex = i;
                        TableColumn<String[], String> column = new TableColumn<>(row[i]);

                        column.setCellValueFactory(cellData ->
                                new SimpleStringProperty(
                                        colIndex < cellData.getValue().length ? cellData.getValue()[colIndex] : ""
                                ));

                        column.setCellFactory(tc -> new TableCell<>() {
                            private final Text text = new Text();

                            {
                                text.wrappingWidthProperty().bind(tc.widthProperty().subtract(10));
                                setGraphic(text);
                                setPrefHeight(Control.USE_COMPUTED_SIZE);
                            }

                            @Override
                            protected void updateItem(String item, boolean empty) {
                                super.updateItem(item, empty);
                                text.setText(empty || item == null ? "" : item);
                                text.setStyle("-fx-fill: white; -fx-font-size: 16px;");
                            }
                        });

                        column.setPrefWidth(350);
                        tableView.getColumns().add(column);
                    }
                    isHeader = false;
                } else {
                    tableView.getItems().add(row);
                }
            }

        } catch (IOException e) {
            e.printStackTrace();
            showErrorMessage("Error reading vacant class file: " + e.getMessage());
            return;
        }


        VBox layout = new VBox(30, new Label("Vacant Classes Per Slot:"), tableView);
        layout.setStyle("-fx-padding: 30px;");
        mainContent.getChildren().add(layout);
    }

    /**
     * Parses a CSV line while respecting quoted values with commas.
     */
    private String[] parseCSVLine(String line) {
        List<String> result = new ArrayList<>();
        StringBuilder current = new StringBuilder();
        boolean inQuotes = false;

        for (int i = 0; i < line.length(); i++) {
            char c = line.charAt(i);

            if (c == '"') {
                inQuotes = !inQuotes;
            } else if (c == ',' && !inQuotes) {
                result.add(current.toString().trim());
                current.setLength(0);
            } else {
                current.append(c);
            }
        }

        result.add(current.toString().trim());
        return result.toArray(new String[0]);
    }


    private void showTimetableTable() {
        mainContent.getChildren().clear();

        if (sectionList.length == 0) {
            showErrorMessage("No sections loaded. Please generate a timetable first.");
            return;
        }

        TabPane tabPane = new TabPane();

        for (String section : sectionList) {
            String fileName = "timetable_" + section + ".csv";
            TableView<String[]> tableView = new TableView<>();
            tableView.setPrefHeight(600);  // increase height for more rows
            VBox.setVgrow(tableView, Priority.ALWAYS);

            try (BufferedReader reader = new BufferedReader(new FileReader(fileName))) {
                String line;
                boolean isHeader = true;

                while ((line = reader.readLine()) != null) {
                    String[] row = line.split(",");

                    if (isHeader) {
                        for (int i = 0; i < row.length; i++) {
                            final int colIndex = i;
                            TableColumn<String[], String> column = new TableColumn<>(row[i]);

                            // Custom cell factory to wrap text and auto adjust row height
                            column.setCellFactory(tc -> {
                                TableCell<String[], String> cell = new TableCell<>() {
                                    private final Text text = new Text();

                                    {
                                        text.wrappingWidthProperty().bind(tc.widthProperty().subtract(10)); // wrap text within cell width minus some padding
                                        setPrefHeight(Control.USE_COMPUTED_SIZE);
                                    }

                                    @Override
                                    protected void updateItem(String item, boolean empty) {
                                        super.updateItem(item, empty);
                                        if (empty || item == null) {
                                            setGraphic(null);
                                        } else {
                                            text.setText(item);
                                            text.setStyle("-fx-fill: white; -fx-font-size: 16px;");
                                            setGraphic(text);
                                        }
                                    }
                                };
                                return cell;
                            });

                            column.setCellValueFactory(cellData -> new javafx.beans.property.SimpleStringProperty(
                                    colIndex < cellData.getValue().length ? cellData.getValue()[colIndex] : ""));
                            column.setPrefWidth(120);
                            tableView.getColumns().add(column);
                        }
                        isHeader = false;
                    } else {
                        tableView.getItems().add(row);
                    }
                }

                Tab tab = new Tab(section, tableView);
                tabPane.getTabs().add(tab);

            } catch (Exception e) {
                e.printStackTrace();
                showErrorMessage("Error reading file for section " + section + ": " + e.getMessage());
            }
        }

        VBox layout = new VBox(20, new Label("📅 Generated Timetables:"), tabPane);
        layout.setStyle("-fx-padding: 30px;");
        VBox.setVgrow(tabPane, Priority.ALWAYS);
        mainContent.getChildren().add(layout);
    }


    private void showErrorMessage(String message) {
        new Alert(AlertType.ERROR, message, ButtonType.OK).showAndWait();
    }

    private void showInfoMessage(String message) {
        new Alert(AlertType.INFORMATION, message, ButtonType.OK).showAndWait();
    }

    private void showLoginScreen(String role) {
        mainContent.getChildren().clear();
        Label loginLabel = new Label(role + " Login");
        loginLabel.getStyleClass().add("login-label"); 

        TextField usernameField = new TextField();
        usernameField.getStyleClass().add("text-field");

        PasswordField passwordField = new PasswordField();
        passwordField.getStyleClass().add("password-field");

        Button loginButton = new Button("Login");
        loginButton.getStyleClass().add("Nbutton");
        loginButton.setOnAction(e -> handleLogin(role, usernameField.getText(), passwordField.getText()));
        
        Label usernameLabel = new Label("Username:");
        usernameLabel.getStyleClass().add("label");
        
        Label passwordLabel = new Label("Password:");
        passwordLabel.getStyleClass().add("label");
        
        VBox loginLayout = new VBox(20, loginLabel, usernameLabel, usernameField,
        		passwordLabel, passwordField, loginButton);
        loginLayout.setStyle("-fx-padding: 60px;");
        mainContent.getChildren().add(loginLayout);
    }

    private void handleLogin(String role, String username, String password) {
        if ("admin".equals(username) && "admin".equals(password)) {
            showAdminDashboard();
        } else {
            showErrorMessage("Invalid credentials");
        }
    }

    public static void main(String[] args) {
        launch(args);
    }
}

