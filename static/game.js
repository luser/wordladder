var debug = false;
var timeout = -1;
function handleSubmit(event)
{
  if (timeout != -1) {
    //cancelTimeout(timeout);
  }
  //event.preventDefault();
}

function handleGameJSON(data)
{
  timeout = -1;
  $.each(data.moves, function(i, m)
         {
           // m.id, m.word, m.parent
           $('#m' + m.parent).parent().append('<li id="l'+m.id+'" style="display:none"><ul><span id="m'+m.id+'" class="move">'+m.word+'</span><form class="hidden" method="POST" action="'+window.location+'/play"><input type="hidden" name="moveid" value="'+m.id+'"><input type="text" name="word"></input></form></ul>');
           $('#m' + m.id).attr('title', 'Click to add a word after this word').click(moveClick).next('form').submit(handleSubmit);
           $('#l' + m.id).show('normal');
         });
  lastmove = data.lastmove;
  // poll again later
  if (!debug)
    pollJSON();
}

function pollJSON()
{
  timeout = setTimeout(function() { $.getJSON(window.location + "?lastmove=" + lastmove, handleGameJSON); }, 2000);
}

function moveClick()
{
  $('form').addClass('hidden');
  $(this).next('form').removeClass('hidden').children('input').get(1).focus();
}

$(document).ready(function()
{
  $('form').addClass('hidden')
    .submit(handleSubmit);
  $('.move').attr('title', 'Click to add a word after this word')
    .click(moveClick);
  // poll JSON
  if (!debug) {
    pollJSON();
  }
  else {
    $(document.body).append('<button id="load">Load JSON</button>');
    $('#load').click(pollJSON);
  }
});
