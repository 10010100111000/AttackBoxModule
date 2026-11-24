<?php
require_once __DIR__ . '/db_connect.php';

final class PayrollAdmin
{
    public function login(string $username, string $password): bool
    {
        // Deliberately preserves the original application's unsafe SQL construction.
        // The database evaluates this against a real MariaDB table.
        $sql = "SELECT * FROM users WHERE username = '" . $username .
            "' AND password = '" . $password . "'";
        $result = $GLOBALS['conn']->query($sql);

        return $result instanceof mysqli_result && $result->num_rows > 0;
    }
}
