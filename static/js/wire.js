var links = [];

function initwires()
{
  var c = document.createElement("canvas");
  c.id = "wirecanvas";
  resizeCanvas(c);
  $(c).css({'position': 'absolute',
	    'left': 0,
	    'top': 0,
	    'z-index': -1
	   });
  document.body.appendChild(c);
}

function addLink(from, to, color)
{
  links.push({'from': from,
	      'to': to,
	      'color': color
	     });
}

function changeLinkColor(from, to, color)
{
  var found = false;
  for (var i=0; i<links.length; i++) {
    if (links[i].from == from && links[i].to == to) {
      links[i].color = color;
      found = true;
      break;
    }
  }
  if (!found)
    addLink(from, to, color);
}

function elementCenter(e)
{
  var o = e.offset();
  return {
    left: o.left + e.outerWidth()/2,
    top: o.top + e.outerHeight()/2
  };
}

function resizeCanvas(c)
{
  c.width = document.documentElement.clientWidth;
  c.height = document.documentElement.scrollHeight;
}

function redrawwires()
{
  var c = $("#wirecanvas").get(0);
  resizeCanvas(c);
  var ctx = c.getContext('2d');
  ctx.clearRect(0,0, c.width, c.height);
  $.each(links, function(i, l) {
	  var f = elementCenter($('#m' + l.from));
	  var t = elementCenter($('#m' + l.to));
	  ctx.beginPath();
		if (Math.abs(f.left, t.left) < 5) f.left = t.left;
		if (t.left < f.left) f.left -= 15;
		if (t.left > f.left) f.left += 15;
	  ctx.moveTo(f.left, f.top);
	  ctx.lineTo(t.left, t.top);
	  ctx.strokeStyle = l.color;
	  ctx.lineWidth = 2.0;
	  ctx.stroke();
	 });

}

$(document).ready(function()
{
  initwires();
  redrawwires();
});

$(window).resize(redrawwires);
