<?php

use Encore\Admin\Facades\Admin;
use Illuminate\Routing\Router;
use Illuminate\Support\Facades\Route;

Route::domain('admin.usage.htb')->group(function () {
    Admin::routes();

    Route::group([
        'prefix' => config('admin.route.prefix'),
        'namespace' => config('admin.route.namespace'),
        'middleware' => config('admin.route.middleware'),
        'as' => 'admin.',
    ], function (Router $router) {
        $router->get('/', 'HomeController@index')->name('home');
    });
});
