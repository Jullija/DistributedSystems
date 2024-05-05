module DynamicPokemons
{
    enum PokemonType
    {
        fire,
        normal,
        water,
        electric,
        grass,
    };


    struct Pokemon
    {
        string name;
        int health;
        int damage;
        PokemonType pokemonType;
    };

    sequence<Pokemon> PokemonSequence;
    dictionary<PokemonType, PokemonSequence> PokemonDictionary;

    interface PokemonInterface
    {
        idempotent PokemonSequence sortByHealth(PokemonSequence pokemon);
        idempotent PokemonDictionary groupByPokemonType(PokemonSequence pokemon);
        idempotent PokemonSequence comparePokemons(PokemonSequence pokemons);
    };
};
