(function(){
  'use strict';
  var form=document.getElementById('bounty-report');
  if(!form)return;
  form.addEventListener('submit',function(ev){
    ev.preventDefault();
    function esc(x){return x.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');}
    var xml='<?xml version="1.0" encoding="ISO-8859-1"?>\n'+
      '<bugreport><title>'+esc(document.getElementById('exploitTitle').value)+'</title>'+
      '<cwe>'+esc(document.getElementById('cwe').value)+'</cwe>'+
      '<cvss>'+esc(document.getElementById('cvss').value)+'</cvss>'+
      '<reward>'+esc(document.getElementById('reward').value)+'</reward></bugreport>';
    fetch('/tracker_diRbPr00f314.php',{
      method:'POST',headers:{'Content-Type':'application/x-www-form-urlencoded'},
      body:new URLSearchParams({data:btoa(xml)}).toString()
    }).then(function(x){return x.text();})
      .then(function(t){document.getElementById('return').innerHTML=t;})
      .catch(function(){document.getElementById('return').textContent='Unable to submit report';});
  });
}());
