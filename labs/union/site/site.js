(function () {
  var form = document.getElementById('eligibility-form');
  if (!form) return;
  form.addEventListener('submit', function (event) {
    event.preventDefault();
    var result = document.getElementById('result');
    var player = document.getElementById('player').value;
    fetch('/index.php', {
      method: 'POST',
      credentials: 'same-origin',
      headers: {'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'},
      body: new URLSearchParams({player: player}).toString()
    }).then(function (response) { return response.text(); })
      .then(function (html) { result.innerHTML = html; })
      .catch(function () { result.textContent = 'Unable to check eligibility.'; });
  });
}());
