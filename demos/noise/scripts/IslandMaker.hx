/**
	Grows an island on the tile map it is on: the Noise behavior beside it
	gives a height for each cell, lower towards the edges so the sea goes
	round, and the height picks the tile: deep water, shallows, sand, grass,
	forest, rock, snow. Grow island makes a new one with a new seed.
**/
@:host(Tilemap)
class IslandMaker extends Component {
	public var columns:Int = 40;
	public var rows:Int = 23;

	override public function onReady():Void grow();

	/**
		@group Island
		@linktext Grow island
		@description Makes the island again from the Noise behavior's seed.
		@ruletext Grow the island
	**/
	@:action
	public function grow():Void {
		var noise:Noise = node.getComponent(Noise);
		if (noise == null) return;
		var cells:Array<Array<Int>> = [];
		for (y in 0...rows) for (x in 0...columns) {
			// Zero in the middle, about one at the edges: the sea comes in from there.
			var dx = (x + 0.5) / columns * 2 - 1, dy = (y + 0.5) / rows * 2 - 1;
			var edge = Math.sqrt(dx * dx + dy * dy);
			var h = noise.heightAt(x, y) * 0.9 + 0.45 - edge * edge * 0.95;
			cells.push([x, y, tileFor(h)]);
		}
		tilemap.setCells(cells);
	}

	static function tileFor(h:Float):Int {
		return h < -0.12 ? 0 : h < 0.0 ? 1 : h < 0.06 ? 2 : h < 0.32 ? 3 : h < 0.56 ? 4 : h < 0.78 ? 5 : 6;
	}
}
