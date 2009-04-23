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
    humanMsg.displayMsg(data.error);
  }
  else {
    // success
    // unfocus textbox
    form.word.blur();
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
  for (var aaa in terminals) {
    terminals[aaa].redrawAllWires();
  };
};


function handleGameJSON(data)
{
  timeout = -1;
  polltime = DEFAULT_POLLTIME;
  if (watchdogtimeout != -1) {
    clearTimeout(watchdogtimeout);
    watchdogtimeout = -1;
  }
  if ('done' in data) {
      done = data.done;
  }
  if (done) {
      //TODO: fancy this up
      document.title += " (finished)";
      $('h1').append(" (finished)");
  }
  $.each(data.moves, function(i, m)
         {
           // m.id, m.word, m.parent
           $('#m' + m.parent).parent().append('<li id="l'+m.id+'" style="display:none"><ul><li><a id="m'+m.id+'" class="move">'+m.word+'</a><form class="hidden" method="POST" action="'+window.location+'/play"><input type="hidden" name="moveid" value="'+m.id+'"><input type="text" name="word" autocomplete="off" autocorrect="off" autocapitalize="off"></input></form></ul>');
           $('#m' + m.id).attr('title', 'Click to add a word after this word').click(moveClick).next('form').submit(handleSubmit);
	   if (done && m.id == data.lastmove) {
	       // this is the winning move
	       $('#m' + m.id).addClass('end');
	   }
           $('#l' + m.id).show('normal');
           setTimeout('drawwire(' + m.id + ', ' + m.parent + ');', 1000);
         });
  lastmove = data.lastmove;
  // poll again later
  if (!debug && !done)
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
  var washidden = $(this).next('form').hasClass('hidden');
  // hide all inputs first
  $('form').addClass('hidden');      
  if (washidden) {
      $(this).next('form').removeClass('hidden').children('input').get(1).focus();      
  }
  else {
      // hidden now, blur it
      $(this).next('form').children('input').get(1).blur();
  }

  event.stopPropagation();
}

$(document).ready(function()
{
  // hide all inputs when you click in empty space
  $(document.body).click(function() {
                           $('form').addClass('hidden');
                         });
  if (!done) {
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
  }
});
