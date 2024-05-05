import sys
import Ice
import DynamicPokemons


class PokemonServer(DynamicPokemons.PokemonInterface):

    def sortByHealth(self, pokemons, current = None):
        sortedPokemons = sorted(pokemons, key=lambda pokemon: pokemon.health)

        print("[SORT BY HEALTH]")
        for pokemon in sortedPokemons:
            print("[{}] {}".format(pokemon.name, pokemon.health))
        return sortedPokemons

    def groupByPokemonType(self, pokemons, current = None):
        #grouped_by_type = {pokemon_type.name: [] for pokemon_type in DynamicPokemons.PokemonType}
        grouped_by_type = {}
        for pokemon in pokemons:
            pokemon_arr = grouped_by_type.get(pokemon.pokemonType, [])
            pokemon_arr.append(pokemon)
            grouped_by_type[pokemon.pokemonType] = pokemon_arr

        print("[GROUP BY TYPE]")
        for key, val in grouped_by_type.items():
            print("[{}] {}".format(key, val))
        return grouped_by_type



    def comparePokemons(self, pokemons, current = None):
        if pokemons[0].health - pokemons[1].damage > pokemons[1].health - pokemons[0].damage:
            print("POKEMON FIGHT")
            print("winner -> {} loser -> {}".format(pokemons[0].name, pokemons[1].name))
            return [pokemons[0], pokemons[1]]
        else:
            print("POKEMON FIGHT")
            print("winner -> {} loser -> {}".format(pokemons[1].name, pokemons[0].name))
            return [pokemons[1], pokemons[0]]



with Ice.initialize(sys.argv) as communicator:
    print("server started...")
    adapter = communicator.createObjectAdapterWithEndpoints("Adapter", "default -p 10000")
    computeObject = PokemonServer()
    adapter.add(computeObject, communicator.stringToIdentity("PokemonObject"))
    adapter.activate()
    communicator.waitForShutdown()