import java.sql.*;
import java.util.*;

public class hwa {
    static String url = "jdbc:postgresql://localhost:5432/cs386d";
    static String user = "postgres";
    static String password = "spring";

    private static String generateRandomText(int length) {
        String characters = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*()_+";
        Random random = new Random();
        StringBuilder sb = new StringBuilder(length);
        for (int i = 0; i < length; i++) {
            int randomIndex = random.nextInt(characters.length());
            sb.append(characters.charAt(randomIndex));
        }
        return sb.toString();
    }

    public static void main(String args[]) {
        String dropTableIfExists = "DROP TABLE IF EXISTS benchmark";
        String createTable = "CREATE TABLE benchmark (" + //
                "theKey INTEGER PRIMARY KEY," + //
                "columnA INTEGER," + //
                "columnB INTEGER," + //
                "filler CHAR(247))";
        String insertRow = "INSERT INTO benchmark VALUES (?,?,?,?)";
        int rows = 10000;
        try {
            // Class.forName("java.sql.Driver");
            Connection connection = DriverManager.getConnection(url, user, password);
            connection.setAutoCommit(false);

            Statement statement = connection.createStatement();
            statement.addBatch(dropTableIfExists);
            statement.addBatch(createTable);
            statement.executeBatch();
            connection.commit();
            // ResultSet rs = statement.executeQuery("SELECT * FROM R");
            // while (rs.next()) {
            // System.out.println(rs.getString(1) + "," + rs.getString(2));
            // }

            System.out.println("Starting");

            long startTime = System.currentTimeMillis();

            Random random = new Random();

            PreparedStatement preparedStatement = connection.prepareStatement(insertRow);

            for (int i = 0; i < rows; i++) {
                System.out.println(i + 1);
                preparedStatement.setInt(1, i);
                preparedStatement.setInt(2, random.nextInt(1, 50000) + 1);
                preparedStatement.setInt(3, random.nextInt(1, 50000) + 1);
                preparedStatement.setString(4, generateRandomText(247));

                preparedStatement.addBatch();
                preparedStatement.executeUpdate();
                if (i % 100 == 0) {
                    // System.out.println(i);
                    preparedStatement.executeBatch();
                    preparedStatement.clearBatch();
                }
            }
            preparedStatement.executeBatch();
            preparedStatement.clearBatch();
            connection.commit();

            // rs.close();
            statement.close();
            connection.close();

            long endTime = System.currentTimeMillis();
            System.out.println("Time: " + (endTime - startTime) + "ms");
        } catch (SQLException e) {
            e.printStackTrace();
        }
    }
}
