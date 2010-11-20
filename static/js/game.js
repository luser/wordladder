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

function handleGameJSON(data)
{
  timeout = -1;
  polltime = DEFAULT_POLLTIME;
  if (watchdogtimeout != -1) {
    clearTimeout(watchdogtimeout);
    watchdogtimeout = -1;
  }

  if ('done' in data && !done) {
      done = data.done;
      //TODO: fancy this up
      document.title += " (finished)";
      $('h1').append(" (finished)");
  }
  var animTimer = -1;
  var numAnims = 0;
  if (data.moves.length > 0) {
      animTimer = setInterval(redrawwires, 100);
  }
  $.each(data.moves, function(i, m)
         {
           // m.id, m.word, m.parent
           if ('username' in m) {
             username = m.username;
           }
           else {
             //FIXME
             username = "user";
           }
					 if ('picture' in m) {
					 	 picture = m.picture;
					 } else {
						 picture = 'http://www.google.com/s2/static/images/NoPicture.gif';
           }
           var html = '<ul id="l'+m.id+'" style="display:none"><li'+(m.bottom?' bottom':'')+'><a id="m'+m.id+'" class="move">'+m.word+'</a><form class="hidden" method="POST" action="'+window.location+'/play"><input type="hidden" name="moveid" value="'+m.id+'"><input type="text" name="word" autocomplete="off" autocorrect="off" autocapitalize="off"></input></form></ul>';
           if (!m.bottom) {
             $('#m' + m.parent).parent().append(html);
           }
           else {
             $('#m' + m.parent).parent().before(html);
           }
           $('#m' + m.id).attr('title', 'Click to add a word after this word').click(moveClick).nextAll('form').submit(handleSubmit);
	   addLink(m.id, m.parent, 'blue');
	   numAnims++;
           $('#l' + m.id).show('normal', function() {
		   numAnims--;
		   if (numAnims <= 0) {
		       clearInterval(animTimer);
		       redrawwires();
		   }
	       });
	   //$('#playinfo').prepend('<span class="log">'+username + " plays " + m.word+"</span>");
			 $.gritter.add({
				 title: username,
				 text: 'played ' + m.word,
				 image: picture,
				 sticky: false
			 });
         });
  if ('done' in data) {
      $.each(data.winningchain, function(i, mid) {
	      $('#m' + mid).addClass('win');
	  });
      for (var i=0; i<data.winningchain.length-1; i++) {
	  changeLinkColor(data.winningchain[i], data.winningchain[i+1], 'red');
      }
  }
  lastmove = data.lastmove;
  // poll again later
  if (!done)
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
  var washidden = $(this).nextAll('form').hasClass('hidden');
  // hide all inputs first
  $('form').addClass('hidden');
  if (washidden) {
      $(this).nextAll('form').removeClass('hidden').children('input').get(1).focus();
  }
  else {
      // hidden now, blur it
      $(this).nextAll('form').children('input').get(1).blur();
  }

  event.stopPropagation();
}

function gritterAdd(g, speed, callback) {
	return callback();
}

$(document).ready(function()
{
	$.extend($.gritter.options, {
		add_at_top: true,
		time: 8000
	});
  
	// hide all inputs when you click in empty space
  $(document.body).click(function() {
                           $('form').addClass('hidden');
                         });
  if (!done) {
      $('form').addClass('hidden')
	  .submit(handleSubmit);
      $('.move').attr('title', 'Click to add a word after this word')
	  .click(moveClick);
      pollJSON();
  }
});
