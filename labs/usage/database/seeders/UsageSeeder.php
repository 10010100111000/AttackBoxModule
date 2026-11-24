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
        $adminHash = '$2y$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2uheWG/igi.';
        if (!Hash::check('password', $adminHash)) {
            throw new \RuntimeException('Admin hash fixture failed verification');
        }

        DB::table('admin_users')->where('username', 'admin')->update([
            'name' => 'Administrator',
            'password' => $adminHash,
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
