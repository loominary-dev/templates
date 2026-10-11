/**
	Smooth random numbers from the perlin library (plugins/libraries/perlin,
	stb_perlin): the same place always gives the same number, and places near
	each other give numbers near each other. For terrain, clouds, wobble,
	wandering. Rules read it as values; scripts call it directly.

	@behavior
	@name Noise
	@category Generate
	@appliesTo Node
**/
class Noise extends Component {
	/** Which world: a different seed is a different pattern. */
	public var seed:Int = 1;

	/**
		How large the features are: smaller is broader.
		@range 0.001 1 0.005
	**/
	public var scale:Float = 0.08;

	/**
		How many layers of detail, each half the size of the last.
		@range 1 8 1
	**/
	public var octaves:Int = 4;

	/**
		@group Noise
		@linktext Height at {0}, {1}
		@description Fractal noise at a place, about -1 to 1: broad hills with smaller ones on them.
		@param x Across.
		@param y Down.
	**/
	@:value
	public function heightAt(x:Float, y:Float):Float
		return Perlin.stb_perlin_fbm_noise3(x * scale, y * scale, seed * 7.31, 2.0, 0.5, octaves);

	/**
		@group Noise
		@linktext Noise at {0}, {1}, {2}
		@description Plain noise at a place and a moment, about -1 to 1: give it the time to make it move.
		@param x Across.
		@param y Down.
		@param t The third axis: time, usually.
	**/
	@:value
	public function noiseAt(x:Float, y:Float, t:Float):Float
		return Perlin.stb_perlin_noise3_seed(x * scale, y * scale, t, 0, 0, 0, seed);

	/**
		@group Noise
		@linktext New seed
		@description A different pattern from now on.
		@ruletext Take a new seed
	**/
	@:action
	public function newSeed():Void seed = 1 + Std.random(100000);
}
