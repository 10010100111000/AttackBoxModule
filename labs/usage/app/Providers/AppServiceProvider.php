<?php

namespace App\Providers;

use Illuminate\Support\Facades\Config;
use Illuminate\Support\ServiceProvider;

class AppServiceProvider extends ServiceProvider
{
    public function register(): void
    {
    }

    public function boot(): void
    {
        Config::set('filesystems.disks.admin', [
            'driver' => 'local',
            'root' => public_path('uploads'),
            'url' => rtrim((string) env('APP_URL', 'http://usage.htb'), '/') . '/uploads',
            'visibility' => 'public',
            'throw' => false,
        ]);
    }
}
