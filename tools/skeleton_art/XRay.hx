/**
	Holding B: every skeleton's pictures fade almost away and its bones are
	drawn, so you can see what moves them. Let go and they come back.
**/
class XRay extends Component {
	/** The input action that shows the bones while it is held. **/
	public var action:String = "Bones";
	/** How much of each picture shows while the bones are shown, 0 to 1. **/
	public var faded:Float = 0.12;

	var showing = false;

	override public function update(dt:Float):Void {
		var want = Input.instance.isCommandOn(action);
		if (want == showing) return;
		showing = want;
		var top:Node = node;
		while (top.parent != null) top = top.parent;
		top.walk(n -> {
			if (Std.downcast(n, Skeleton) == null) return;
			n.walk(c -> {
				var b = Std.downcast(c, Bone);
				if (b != null) b.showInGame = showing;
				else if (c != n && Std.isOfType(c, Sprite)) c.opacity = showing ? faded : 1;
			});
		});
	}
}
