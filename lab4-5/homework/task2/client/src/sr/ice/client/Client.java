package sr.ice.client;

import DynamicPokemons.*;
import com.zeroc.Ice.*;
import com.zeroc.Ice.Object;

import java.lang.Exception;
import java.util.*;

public class Client {
	private final com.zeroc.Ice.Communicator communicator;
	private final ObjectPrx proxy;
	private Pokemon[] pokemons;

	public Client(String[] args){
		communicator = com.zeroc.Ice.Util.initialize(args);
		proxy = communicator.stringToProxy("PokemonObject:default -p 10000");
		generatePokemons();
	}

	public void generatePokemons(){
		List<Pokemon> pokemonsArrayList = new ArrayList<>();

		pokemonsArrayList.add(new Pokemon("Szymon", 420, 69, PokemonType.fire));
		pokemonsArrayList.add(new Pokemon("Alex", 300, 50, PokemonType.fire));
		pokemonsArrayList.add(new Pokemon("Mia", 200, 80, PokemonType.normal));
		pokemonsArrayList.add(new Pokemon("Liam", 450, 70, PokemonType.water));
		pokemonsArrayList.add(new Pokemon("Zoe", 330, 60, PokemonType.electric));
		pokemonsArrayList.add(new Pokemon("Noah", 280, 90, PokemonType.grass));
		pokemonsArrayList.add(new Pokemon("Eva", 350, 85, PokemonType.fire));
		pokemonsArrayList.add(new Pokemon("Olivia", 220, 75, PokemonType.normal));
		pokemonsArrayList.add(new Pokemon("Luke", 400, 65, PokemonType.water));
		pokemonsArrayList.add(new Pokemon("Sophia", 310, 55, PokemonType.electric));
		pokemonsArrayList.add(new Pokemon("Jack", 260, 95, PokemonType.grass));
		pokemonsArrayList.add(new Pokemon("Dominik", 310, 55, PokemonType.electric));
		pokemonsArrayList.add(new Pokemon("Julia", 260, 95, PokemonType.water));
		pokemonsArrayList.add(new Pokemon("Ania", 220, 35, PokemonType.grass));

		pokemons = pokemonsArrayList.toArray(new Pokemon[0]);
	}

	public void comparePokemons(){
		if (pokemons.length < 2) {
			System.out.println("Not enough Pokémon for comparison.");
			return;
		}

		Random random = new Random();
		int firstIndex = random.nextInt(pokemons.length);
		int secondIndex;
		do {
			secondIndex = random.nextInt(pokemons.length);
		} while (secondIndex == firstIndex);

		Pokemon pokemon1 = pokemons[firstIndex];
		Pokemon pokemon2 = pokemons[secondIndex];

		try {
			// Initialize OutputStream for Ice communication
			OutputStream out = new OutputStream(communicator);
			out.startEncapsulation();

			// Write selected Pokémon to the stream
			PokemonSequenceHelper.write(out, new Pokemon[]{pokemon1, pokemon2});
			out.endEncapsulation();

			// Prepare the byte array for Ice invoke
			byte[] inParams = out.finished();

			// Invoke the Ice method
			Object.Ice_invokeResult invokeResult = proxy.ice_invoke("comparePokemons", OperationMode.Idempotent, inParams);

			if (invokeResult.returnValue) {
				InputStream in = new InputStream(communicator, invokeResult.outParams);
				in.startEncapsulation();
				// Assuming the response includes some kind of result or comparison data
				Pokemon[] pokemonWinner = PokemonSequenceHelper.read(in);
				in.endEncapsulation();

				System.out.println("Comparison result: " + pokemonWinner[0]);
			} else {
				System.out.println("Failed to compare Pokémon.");
			}
		} catch (Exception e) {
			e.printStackTrace();
			System.out.println("An error occurred during the comparison process.");
		}
	}

	public void pokemonSort() {
		OutputStream out = new OutputStream(communicator);
		out.startEncapsulation();

		PokemonSequenceHelper.write(out, pokemons);
		out.endEncapsulation();

		byte[] inParams = out.finished();
		Object.Ice_invokeResult invokeResult = proxy.ice_invoke("sortByHealth", OperationMode.Idempotent, inParams);

		if (invokeResult.returnValue) {
			InputStream in = new com.zeroc.Ice.InputStream(communicator, invokeResult.outParams);
			in.startEncapsulation();
			Pokemon[] sortedPokemons = PokemonSequenceHelper.read(in);
			in.endEncapsulation();

			System.out.println("[SORTED BY HEALTH]");
			for (Pokemon pokemon : sortedPokemons) {
				System.out.println("[{" + pokemon.name+ "}] " + pokemon.health);
			}
		} else {
			System.out.println("[SORTING BY HEALTH] something went wrong.");
		}
	}

	public void pokemonGroup() {
		OutputStream out = new OutputStream(communicator);
		out.startEncapsulation();

		PokemonSequenceHelper.write(out, pokemons);
		out.endEncapsulation();

		byte[] inParams = out.finished();
		Object.Ice_invokeResult invokeResult = proxy.ice_invoke("groupByPokemonType", OperationMode.Idempotent, inParams);

		if (invokeResult.returnValue) {
			InputStream in = new InputStream(communicator, invokeResult.outParams);
			in.startEncapsulation();
			Map<PokemonType, Pokemon[]> groupedByType = PokemonDictionaryHelper.read(in);
			in.endEncapsulation();

			System.out.println("[GROUP BY TYPE]");
			for (Map.Entry<PokemonType, Pokemon[]> key_val : groupedByType.entrySet()) {
				PokemonType type = key_val.getKey();
				Pokemon[] pokemons1 = key_val.getValue();
				System.out.println("type: " + type);
				System.out.println(pokemons1);
			}
		} else {
			System.out.println("[GROUP BY TYPE] something went wrong.");
		}
	}


	public void start() {
		Scanner scanner = new Scanner(System.in);

		try {
			while(true) {
				System.out.println();
				System.out.println("'fight' - fight between two pokemons");
				System.out.println("'sort' - sort by pokemons' health");
				System.out.println("'group' - group by pokemons' type");

				String input = scanner.nextLine().toLowerCase();
				switch (input) {
					case "fight" -> comparePokemons();
					case "sort" -> pokemonSort();
					case "group" -> pokemonGroup();
					default -> System.out.println("wrong input. 'fight', 'sort' or 'group' expected");
				}
			}
		} catch (com.zeroc.Ice.LocalException ex) {
			ex.printStackTrace();
			System.out.println("Something went wrong.");
		} finally {
			scanner.close();
		}
	}


	public static void main(String[] args) {
		Client client = new Client(args);
		client.start();
	}
}