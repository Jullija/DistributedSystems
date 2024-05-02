package main

import (
    "bufio"
    "context"
    "fmt"
    "log"
    "os"
    "strings"
    "time"

    "google.golang.org/grpc"
    proto "example.com/myproject/client/myproject/proto"
)

func mapLocation(input string) (proto.Location, bool) {
    switch input {
    case "CRACOW":
        return proto.Location_CRACOW, true
    case "LONDON":
        return proto.Location_LONDON, true
    case "SEDZISZOW":
        return proto.Location_SEDZISZOW, true
    case "ZURICH":
        return proto.Location_ZURICH, true
    case "LOS_ANGELES":
        return proto.Location_LOS_ANGELES, true
    default:
        return 0, false
    }
}

func mapType(input string) (proto.EventType, bool) {
    switch input {
    case "SPORT_EVENT":
        return proto.EventType_SPORT_EVENT, true
    case "CONCERT":
        return proto.EventType_CONCERT, true
    case "MEETING":
        return proto.EventType_MEETING, true
    default:
        return 0, false
    }
}

func getClientSubscriptions(client proto.EventServiceClient, clientID int32) {
    ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
    defer cancel()


    req := &proto.ClientSubscriptionsRequest{ClientId: clientID}


    resp, err := client.GetClientSubscriptions(ctx, req)
    if err != nil {
        log.Fatalf("Could not get subscriptions: %v", err)
    }


    fmt.Printf("Client %d is subscribed to the following events:\n", clientID)
    for _, event := range resp.SubscribedEvents {
        fmt.Printf("Event ID: %d, Type: %s, Location: %s, Description: %s, Max Attendees: %d\n",
            event.EventId, proto.EventType_name[int32(event.Type)], proto.Location_name[int32(event.Location)], event.Description, event.MaxAttendees)
    }
}

func getClientName() string{
    reader := bufio.NewReader(os.Stdin)
    fmt.Print("Enter your nickname: ")
    name, _ := reader.ReadString('\n')
    return name
}



func parseLocation(argument string, client proto.EventServiceClient, clientId int32, clientName string){
    location, ok := mapLocation(argument)
    if !ok {
        fmt.Println("Invalid location. Please try again.")
        return
    }

    request := &proto.ClientSubscribeLocationRequest{
        ClientId:   int32(clientId),
        ClientName: clientName,
        Location:   location,
    }

    ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
    defer cancel()

    response, err := client.ClientSubscribeLocation(ctx, request)
    if err != nil {
        log.Printf("Error subscribing to location: %v", err)
        return
    }


    for _, event := range response.EventsList {
        fmt.Printf("Event ID: %d, Type: %s, Location: %s\n", event.EventId, proto.EventType_name[int32(event.Type)], proto.Location_name[int32(event.Location)])
    }
}


func parseType(argument string, client proto.EventServiceClient, clientId int32, clientName string) {
    eventType, ok := mapType(argument)
    if !ok {
        fmt.Println("Invalid type. Please try again.")
        return
    }
    request := &proto.ClientSubscribeTypeRequest{
        ClientId:   clientId,
        ClientName: clientName,
        Type:       eventType,
    }
    ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
    defer cancel()
    response, err := client.ClientSubscribeType(ctx, request)
    if err != nil {
        log.Printf("Error subscribing to type: %v", err)
        return
    }

    for _, event := range response.EventsList {
        fmt.Printf("Event ID: %d, Type: %s, Location: %s\n", event.EventId, proto.EventType_name[int32(event.Type)], proto.Location_name[int32(event.Location)])
    }
}


func getInputs(client proto.EventServiceClient, clientId int32, clientName string) {
    reader := bufio.NewScanner(os.Stdin)
    for {
        fmt.Print("<subLocation location_name> -> location subscribe, <subType event_type> -> type subscribe, <subId id> -> id subscribe, <subCheck> -> see you subscription\n")
        fmt.Print("Command: ")
        if reader.Scan() {
            input := reader.Text()
            parts := strings.Fields(input)
            if len(parts) < 2 && parts[0] != "subCheck" {
                fmt.Println("Invalid command format. Use <subLocation location_name>, <subType event_type>, <subId id>, <subCheck>.")
                continue
            }

            command := parts[0]
            argument := strings.Join(parts[1:], " ")


            switch command{
            case "subLocation":
                parseLocation(argument, client, clientId, clientName)
            case "subType":
                parseType(argument, client, clientId, clientName)
//             case "subId":
//                 parseId(argument, client, clientId, clientName)
            case "subCheck":
                getClientSubscriptions(client, clientId)
            case "quit":
                fmt.Println("Closing connection. Thank you for listening to my TedTalk.")
                return
            default:
                fmt.Println("Invalid option, please choose again. Use <subLocation location_name>, <subType event_type>, <subId id>.")
            }
        }
    }
}



func main() {
    conn, err := grpc.Dial("localhost:50051", grpc.WithInsecure(), grpc.WithBlock())
    if err != nil {
        log.Fatalf("did not connect: %v", err)
    }
    defer conn.Close()

    c := proto.NewEventServiceClient(conn)
    ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second) // Extended deadline
    defer cancel()

    clientName := getClientName()
    req := proto.ClientConnectsRequest{ClientName: clientName}
    r, err := c.ClientConnects(ctx, &req)
    if err != nil {
        log.Fatalf("could not connect: %v", err)
    }
    log.Printf("Client ID: %d", r.ClientId)


    getInputs(c, r.ClientId, clientName)
}

