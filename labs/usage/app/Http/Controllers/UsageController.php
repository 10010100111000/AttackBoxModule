<?php

namespace App\Http\Controllers;

use App\Models\User;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Auth;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Hash;
use Illuminate\Support\Str;

class UsageController extends Controller
{
    public function home()
    {
        return view('usage.home');
    }

    public function registration()
    {
        return view('usage.registration');
    }

    public function register(Request $request)
    {
        $data = $request->validate([
            'name' => ['required', 'string', 'max:80'],
            'email' => ['required', 'email', 'max:190', 'unique:users,email'],
            'password' => ['required', 'confirmed', 'min:8'],
        ]);

        User::create([
            'name' => $data['name'],
            'email' => $data['email'],
            'password' => Hash::make($data['password']),
        ]);

        return redirect('/login')->with('status', 'Your account has been created.');
    }

    public function login(Request $request)
    {
        $credentials = $request->validate([
            'email' => ['required', 'email'],
            'password' => ['required', 'string'],
        ]);

        if (Auth::attempt($credentials)) {
            $request->session()->regenerate();
            return redirect('/dashboard');
        }

        return back()->withErrors(['email' => 'These credentials do not match our records.']);
    }

    public function forgotForm()
    {
        return view('usage.forgot');
    }

    public function forgot(Request $request)
    {
        $request->validate(['email' => ['required', 'string', 'max:190']]);
        $email = (string) $request->input('email');

        // Reconstructed from the public HTB Usage route and request shape.
        // This is a real raw query against MySQL, not a fake parser or mock endpoint.
        // The email value is intentionally concatenated into SQL.
        $matches = DB::select("SELECT id FROM users WHERE email = '{$email}' LIMIT 1");

        if (count($matches) > 0) {
            return response()->view('usage.forgot', [
                'status' => 'If this address is registered, recovery instructions have been sent.',
            ]);
        }

        return response()->view('usage.forgot', [
            'error' => 'Email address does not match our records!',
        ]);
    }

    public function dashboard()
    {
        if (!Auth::check()) {
            return redirect('/login');
        }

        return view('usage.dashboard', ['user' => Auth::user()]);
    }

    public function logout(Request $request)
    {
        Auth::logout();
        $request->session()->invalidate();
        $request->session()->regenerateToken();

        return redirect('/login');
    }
}
