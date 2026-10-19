/**
	Clouds over the island: a grid of soft white dots, each as opaque as the
	Noise behavior says at its place and the moment, so the clouds drift and
	change shape. Weather on and off fades them in and out.
**/
class Weather extends Component {
	public var speed:Float = 0.25;
	var clouds:Array<Node> = [];
	var t = 0.0;
	var amount = 1.0;
	var wanted = 1.0;

	override public function onReady():Void {
		for (y in 0...13) for (x in 0...22) {
			var c = new Cloud("Cloud");
			c.x = -320 + x * 32;
			c.y = -180 + y * 32;
			c.scaleX = c.scaleY = 2.2;
			node.addChild(c);
			clouds.push(c);
		}
	}

	override public function update(dt:Float):Void {
		var noise:Noise = node.getComponent(Noise);
		if (noise == null) return;
		t += dt * speed;
		amount += (wanted - amount) * Math.min(1, dt * 2);
		for (c in clouds) {
			var n = noise.noiseAt(c.x + t * 30, c.y, t);
			c.opacity = Math.max(0, Math.min(0.85, (n - 0.05) * 2.2)) * amount;
		}
	}

	/**
		@group Weather
		@linktext Set weather {0}
		@description Fades the clouds in or out.
		@ruletext Set weather {0}
		@param on On or off.
	**/
	@:action
	public function setWeather(on:Bool):Void wanted = on ? 1 : 0;

	/**
		@group Weather
		@linktext Switch the weather
		@description Clouds if there are none, none if there are.
		@ruletext Switch the weather
	**/
	@:action
	public function toggle():Void wanted = wanted > 0.5 ? 0 : 1;

	/**
		@group Weather
		@linktext Weather is on
		@description True while the clouds are wanted.
		@ruletext Weather is on
	**/
	@:condition
	public function isOn():Bool return wanted > 0.5;
}
