<?php

namespace Database\Seeders;

use Illuminate\Database\Seeder;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Hash;
use Illuminate\Support\Str;

class UsageSeeder extends Seeder
{
    public function run(): void
    {
        // This well-known bcrypt hash corresponds to "password". The player
        // must obtain it through the genuine blind SQLi and crack it offline.
        $adminHash = '$2y$10$irkWuvMbCYgAzMFXgCa7MerOhNRwEw.PKNjup3puiylVKRmo3BEXC';
        if (!Hash::check('password', $adminHash)) {
            throw new \RuntimeException('Admin hash fixture failed verification');
        }

        $databaseFlagPath = '/opt/usage/flags/database.txt';
        if (!is_readable($databaseFlagPath)) {
            throw new \\RuntimeException('Versioned database Flag seed is missing');
        }
        $databaseFlag = trim((string) file_get_contents($databaseFlagPath));
        if (!preg_match('/^TTP\\{[a-z2-7]{16}\\}$/', $databaseFlag)) {
            throw new \\RuntimeException('Versioned database Flag seed has an invalid format');
        }

        DB::table('admin_users')->where('username', 'admin')->update([
            'name' => 'Administrator',
            'password' => $adminHash,
            // Laravel-admin's native persistent-login token column is the SQLi objective.
            'remember_token' => $databaseFlag,
            'updated_at' => now(),
        ]);

        DB::table('users')->updateOrInsert(
            ['email' => 'member@usage.htb'],
            [
                'name' => 'Community Member',
                'password' => Hash::make(Str::random(48)),
                'created_at' => now(),
                'updated_at' => now(),
            ]
        );
    }
}
