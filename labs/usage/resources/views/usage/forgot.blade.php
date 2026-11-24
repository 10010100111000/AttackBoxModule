@extends('layouts.usage')
@section('title', 'Password recovery')
@section('content')
<div class="card">
    <h1>Forgot password</h1><p class="muted">Enter the email address associated with your account.</p>
    @if(isset($status))<div class="notice">{{ $status }}</div>@endif
    @if(isset($error))<div class="notice error">{{ $error }}</div>@endif
    @if($errors->any())<div class="notice error">{{ $errors->first() }}</div>@endif
    <form method="post" action="/forget-password">
        @csrf
        <label for="email">Email address</label>
        <input id="email" type="text" name="email" value="{{ old('email') }}" required>
        <button type="submit">Send recovery email</button>
    </form>
    <div class="links"><a href="/login">Back to login</a><a href="/registration">Create account</a></div>
</div>
@endsection
