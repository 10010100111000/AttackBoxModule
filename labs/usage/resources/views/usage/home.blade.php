@extends('layouts.usage')
@section('title', 'Login')
@section('content')
<div class="card">
    <h1>Welcome back</h1>
    <p class="muted">Sign in to continue to Daily Blogs.</p>
    @if(session('status'))<div class="notice">{{ session('status') }}</div>@endif
    @if($errors->any())<div class="notice error">{{ $errors->first() }}</div>@endif
    <form method="post" action="/login">
        @csrf
        <label for="email">Email address</label>
        <input id="email" type="email" name="email" value="{{ old('email') }}" required>
        <label for="password">Password</label>
        <input id="password" type="password" name="password" required>
        <button type="submit">Sign in</button>
    </form>
    <div class="links"><a href="/forget-password">Forgot password?</a><a href="/registration">Create account</a></div>
</div>
@endsection
