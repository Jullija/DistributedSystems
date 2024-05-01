## Zadanie A.2 - Subskrypcja na zdarzenia
Wynikiem prac ma być aplikacja klient-serwer w technologii gRPC. Klient powinien móc dokonywać subskrypcji na pewnego rodzaju zdarzenia. To, o czym mają one informować, jest w gestii Wykonawcy, np. o nadchodzącym wydarzeniu, którym jesteśmy zainteresowani ze względu na miejsce, czas, tematykę itp, o osiągnięciu określonych w żądaniu warunków pogodowych w danym miejscu, itp.


Dodatkowe informacje i wymagania:


1. Na pojedyncze zdarzenie może się zasubskrybować wielu odbiorców naraz.
2. Może istnieć wiele niezależnych subskrypcji (tj. np. na wiele różnych instancji spotkań). 
3. Projektując protokół komunikacji pomiędzy stronami należy odpowiednio wykorzystać mechanizm strumieniowania (stream) - niedopuszczalny jest polling.
4. Wiadomości mogą nadchodzić z różnymi odstępami czasowymi (w rzeczywistości nawet bardzo długimi), jednak na potrzeby demonstracji rozwiązania należy przyjąć interwał rzędu pojedynczych sekund.
5. W definicji wiadomości przesyłanych do klienta należy wykorzystać pola liczbowe, enum, string, message - wraz z co najmniej jednym modyfikatorem repeated. Etap subskrypcji powinien w jakiś sposób precyzować, które powiadomienia danej usługi (spośród wszystkich) są dla odbiorcy interesujące (np. obejmować wskazanie miasta, którego warunki pogodowe nas interesują) i dany odbiorca powinien otrzymywać wyłącznie interesujące go powiadomienia.
6. Dla uproszczenia realizacji zadania można (nie trzeba) pominąć funkcjonalność samego tworzenia instancji wydarzeń lub miejsc, których dotyczy subskrypcja i notyfikacja - może to być zawarte w pliku konfiguracyjnym, a nawet kodzie źródłowym strony serwerowej. Treść wysyłanych zdarzeń może być wynikiem działania bardzo prostego generatora.
7. W realizacji należy zadbać o odporność komunikacji na błędy sieciowe (które można symulować czasowym gwałtownym wyłączeniem klienta lub serwera lub włączeniem zapory sieciowej). Ustanie przerwy w łączności sieciowej musi pozwolić na ponowne ustanowienie komunikacji bez konieczności restartu procesów. Wiadomości przeznaczone do dostarczenia powinny być buforowane przez serwer do czasu ponownego ustanowienia łączności. Rozwiązanie musi być także "NAT-friendly" (tj. uwzględniać rozważane na laboratorium sytuacje związane z translacją adresów, w tym podtrzymywaniem aktywności w kanale komunikacyjnym).


Technologia middleware: gRPC
Języki programowania: dwa różne (jeden dla klienta, drugi dla serwera)
Maksymalna punktacja: 12


## How to run
In task1 run

```python -m grpc_tools.protoc -I. --python_out=server --grpc_python_out=server proto/event.proto```


```protoc --proto_path=proto --go_out=client/myproject/proto --go-grpc_out=client/myproject/proto --go_opt=paths=source_relative --go-grpc_opt=paths=source_relative proto/event.proto```

then in server directory run

```python server.py```

and in client directory

```go run client.go```






go mod tidy
go build -o client_app ./client
./client_app  



[//]: # (export PATH=$PATH:$&#40;go env GOPATH&#41;/bin)

[//]: # (chmod +x $&#40;go env GOPATH&#41;/bin/protoc-gen-go)

[//]: # (chmod +x $&#40;go env GOPATH&#41;/bin/protoc-gen-go-grpc)



