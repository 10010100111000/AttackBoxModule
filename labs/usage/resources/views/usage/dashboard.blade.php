@extends('layouts.usage')
@section('title', 'Dashboard')
@section('content')
<div class="card"><h1>Your dashboard</h1><p class="muted">Signed in as {{ $user->email }}.</p><form method="post" action="/logout">@csrf<button type="submit">Sign out</button></form></div>
@endsection
