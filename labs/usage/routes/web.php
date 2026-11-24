<?php

use App\Http\Controllers\UsageController;
use Illuminate\Support\Facades\Route;

Route::domain('usage.htb')->group(function () {
    Route::get('/', [UsageController::class, 'home'])->name('home');
    Route::get('/login', [UsageController::class, 'home'])->name('login');
    Route::post('/login', [UsageController::class, 'login'])->name('login.submit');
    Route::get('/registration', [UsageController::class, 'registration'])->name('registration');
    Route::post('/registration', [UsageController::class, 'register'])->name('registration.submit');
    Route::get('/forget-password', [UsageController::class, 'forgotForm'])->name('password.request');
    Route::post('/forget-password', [UsageController::class, 'forgot'])->name('password.email');
    Route::get('/dashboard', [UsageController::class, 'dashboard'])->name('dashboard');
    Route::post('/logout', [UsageController::class, 'logout'])->name('logout');
});
