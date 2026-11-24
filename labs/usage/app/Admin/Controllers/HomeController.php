<?php

namespace App\Admin\Controllers;

use Encore\Admin\Controllers\AdminController;
use Encore\Admin\Layout\Content;

class HomeController extends AdminController
{
    public function index(Content $content)
    {
        return $content
            ->title('Dashboard')
            ->description('Daily Blogs administration')
            ->body('<div class="box"><div class="box-body"><h3>Welcome back</h3><p>Manage your blog profile and site settings.</p><p><a href="' . admin_url('auth/setting') . '">User settings</a></p></div></div>');
    }
}
