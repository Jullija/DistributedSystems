package main

import (
    "context"
    "log"
    "time"

    "google.golang.org/grpc"
    proto "example.com/myproject/client/myproject/proto"
)

func main() {
    conn, err := grpc.Dial("localhost:50051", grpc.WithInsecure(), grpc.WithBlock())
    if err != nil {
        log.Fatalf("did not connect: %v", err)
    }
    defer conn.Close()

    c := proto.NewEventServiceClient(conn) // Use the 'proto' alias

    ctx, cancel := context.WithTimeout(context.Background(), time.Second)
    defer cancel()

    req := proto.ClientConnectsRequest{ClientName: "GoClient"} // Use 'proto' for types
    r, err := c.ClientConnects(ctx, &req)
    if err != nil {
        log.Fatalf("could not connect: %v", err)
    }
    log.Printf("Client ID: %d", r.ClientId)
    log.Printf("Events: %v", r.Events)
}
