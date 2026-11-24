@extends('layouts.usage')
@section('title', 'Create account')
@section('content')
<div class="card">
    <h1>Create an account</h1><p class="muted">Join the Daily Blogs community.</p>
    @if($errors->any())<div class="notice error">{{ $errors->first() }}</div>@endif
    <form method="post" action="/registration">
        @csrf
        <label>Name</label><input name="name" value="{{ old('name') }}" required>
        <label>Email address</label><input type="email" name="email" value="{{ old('email') }}" required>
        <label>Password</label><input type="password" name="password" required>
        <label>Confirm password</label><input type="password" name="password_confirmation" required>
        <button type="submit">Create account</button>
    </form>
    <div class="links"><a href="/login">Back to login</a></div>
</div>
@endsection
