YAHOO.env.classMap = {"WireIt.Container": "WireIt", "WireIt.FormContainer": "WireIt", "WireIt.CanvasElement": "WireIt", "WireIt.util.DD": "WireIt", "WireIt.ImageContainer": "WireIt", "WireIt.Scissors": "WireIt", "WireIt.util.TerminalOutput": "WireIt", "WireIt.WiringEditor": "WireIt", "WireIt.Layer": "WireIt", "WireIt.LayerMap": "WireIt", "WireIt.WireIt": "WireIt", "WireIt.util.DDResize": "WireIt", "WireIt.Wire": "WireIt", "WireIt.util.Anim": "WireIt", "inputEx.Field": "WireIt", "WireIt.Terminal": "WireIt", "WireIt.util.TerminalInput": "WireIt", "WireIt.TerminalProxy": "WireIt", "inputEx.BaseField": "WireIt"};

YAHOO.env.resolveClass = function(className) {
    var a=className.split('.'), ns=YAHOO.env.classMap;

    for (var i=0; i<a.length; i=i+1) {
        if (ns[a[i]]) {
            ns = ns[a[i]];
        } else {
            return null;
        }
    }

    return ns;
};
