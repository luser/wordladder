var debug = false;
var DEFAULT_POLLTIME = 2000;
var timeout = -1;
var watchdogtimeout = -1;
var polltime = DEFAULT_POLLTIME;
var terminals = [];

function handleSubmit(event)
{
  var form = this;
  if (timeout != -1) {
    clearTimeout(timeout);
    timeout = -1;
  }
  if (watchdogtimeout != -1) {
    clearTimeout(watchdogtimeout);
    watchdogtimeout = -1;
  }
  $.ajax({type: 'POST',
          url: document.location.href,
          data: {'lastmove': lastmove,
                   'word': this.word.value,
                   'moveid': this.moveid.value
                  },
          dataType: 'json',
          beforeSend: function(req) {
            req.setRequestHeader('Accept', 'text/json');
          },
          success: function(data) { handlePlayResponse(form, data); },
          error: function(req, err, ex) { handlePlayError(form, err); }
         });
  //TODO: throbber, color box, etc?
  event.preventDefault();
}

function handlePlayResponse(form, data)
{
  if ('error' in data) {
    //TODO: something more subtle, maybe fade in too
    $(form.word).addClass('error');
    //TODO: show data.error as text somewhere
  }
  else {
    // success
    form.word.value = '';
    $(form.word).removeClass('error');
    $(form).addClass('hidden');
  }
  handleGameJSON(data);
}

function handlePlayError(form, err)
{
  //TODO: network error icon or something
}


function drawwire(mid, mparent) {
  terminals[mid] = new WireIt.Terminal(document.getElementById('m' + mid), {editable: false, offsetPosition: [0,-6]});
  var wire = new WireIt.Wire(terminals[mparent], terminals[mid], document.body, {drawingMethod: 'arrows'});
  terminals[mparent].redrawAllWires();
};


function handleGameJSON(data)
{
  timeout = -1;
  polltime = DEFAULT_POLLTIME;
  if (watchdogtimeout != -1) {
    clearTimeout(watchdogtimeout);
    watchdogtimeout = -1;
  }
  //TODO: handle data.done for end-of-game
  $.each(data.moves, function(i, m)
         {
           // m.id, m.word, m.parent
           $('#m' + m.parent).parent().append('<li id="l'+m.id+'" style="display:none"><ul><li><span id="m'+m.id+'" class="move">'+m.word+'</span><form class="hidden" method="POST" action="'+window.location+'/play"><input type="hidden" name="moveid" value="'+m.id+'"><input type="text" name="word"></input></form></ul>');
           $('#m' + m.id).attr('title', 'Click to add a word after this word').click(moveClick).next('form').submit(handleSubmit);
           $('#l' + m.id).show('normal');
           setTimeout('drawwire(' + m.id + ', ' + m.parent + ');', 1000);
         });
  lastmove = data.lastmove;
  // poll again later
  if (!debug)
    pollJSON();
}

function watchdog()
{
  // our request didn't come back?
  // bump up our timeout a bit and try again
  polltime = parseInt(polltime * 1.5);
  pollJSON();
  //TODO: show a network connectivity fail icon?
}

function pollJSON()
{
  timeout = setTimeout(function() { $.getJSON(window.location + "?lastmove=" + lastmove, handleGameJSON); }, polltime);
  watchdogtimeout = setTimeout(watchdog, polltime * 2);
}

function moveClick(event)
{
  $('form').addClass('hidden');
  $(this).next('form').removeClass('hidden').children('input').get(1).focus();
  event.stopPropagation();
}

$(document).ready(function()
{
  // hide all inputs when you click in empty space
  $(document.body).click(function() {
                           $('form').addClass('hidden');
                         });
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
