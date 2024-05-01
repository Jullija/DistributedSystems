// Code generated by protoc-gen-go-grpc. DO NOT EDIT.
// versions:
// - protoc-gen-go-grpc v1.3.0
// - protoc             v5.26.1
// source: event.proto

package proto

import (
	context "context"
	grpc "google.golang.org/grpc"
	codes "google.golang.org/grpc/codes"
	status "google.golang.org/grpc/status"
)

// This is a compile-time assertion to ensure that this generated file
// is compatible with the grpc package it is being compiled against.
// Requires gRPC-Go v1.32.0 or later.
const _ = grpc.SupportPackageIsVersion7

const (
	EventService_ClientConnects_FullMethodName          = "/event.EventService/ClientConnects"
	EventService_ClientSubscribeLocation_FullMethodName = "/event.EventService/ClientSubscribeLocation"
)

// EventServiceClient is the client API for EventService service.
//
// For semantics around ctx use and closing/ending streaming RPCs, please refer to https://pkg.go.dev/google.golang.org/grpc/?tab=doc#ClientConn.NewStream.
type EventServiceClient interface {
	// client connects
	ClientConnects(ctx context.Context, in *ClientConnectsRequest, opts ...grpc.CallOption) (*ClientConnectsResponse, error)
	// client subscribe based on location
	ClientSubscribeLocation(ctx context.Context, in *ClientSubscribeLocationRequest, opts ...grpc.CallOption) (*ClientSubscribeLocationResponse, error)
}

type eventServiceClient struct {
	cc grpc.ClientConnInterface
}

func NewEventServiceClient(cc grpc.ClientConnInterface) EventServiceClient {
	return &eventServiceClient{cc}
}

func (c *eventServiceClient) ClientConnects(ctx context.Context, in *ClientConnectsRequest, opts ...grpc.CallOption) (*ClientConnectsResponse, error) {
	out := new(ClientConnectsResponse)
	err := c.cc.Invoke(ctx, EventService_ClientConnects_FullMethodName, in, out, opts...)
	if err != nil {
		return nil, err
	}
	return out, nil
}

func (c *eventServiceClient) ClientSubscribeLocation(ctx context.Context, in *ClientSubscribeLocationRequest, opts ...grpc.CallOption) (*ClientSubscribeLocationResponse, error) {
	out := new(ClientSubscribeLocationResponse)
	err := c.cc.Invoke(ctx, EventService_ClientSubscribeLocation_FullMethodName, in, out, opts...)
	if err != nil {
		return nil, err
	}
	return out, nil
}

// EventServiceServer is the server API for EventService service.
// All implementations must embed UnimplementedEventServiceServer
// for forward compatibility
type EventServiceServer interface {
	// client connects
	ClientConnects(context.Context, *ClientConnectsRequest) (*ClientConnectsResponse, error)
	// client subscribe based on location
	ClientSubscribeLocation(context.Context, *ClientSubscribeLocationRequest) (*ClientSubscribeLocationResponse, error)
	mustEmbedUnimplementedEventServiceServer()
}

// UnimplementedEventServiceServer must be embedded to have forward compatible implementations.
type UnimplementedEventServiceServer struct {
}

func (UnimplementedEventServiceServer) ClientConnects(context.Context, *ClientConnectsRequest) (*ClientConnectsResponse, error) {
	return nil, status.Errorf(codes.Unimplemented, "method ClientConnects not implemented")
}
func (UnimplementedEventServiceServer) ClientSubscribeLocation(context.Context, *ClientSubscribeLocationRequest) (*ClientSubscribeLocationResponse, error) {
	return nil, status.Errorf(codes.Unimplemented, "method ClientSubscribeLocation not implemented")
}
func (UnimplementedEventServiceServer) mustEmbedUnimplementedEventServiceServer() {}

// UnsafeEventServiceServer may be embedded to opt out of forward compatibility for this service.
// Use of this interface is not recommended, as added methods to EventServiceServer will
// result in compilation errors.
type UnsafeEventServiceServer interface {
	mustEmbedUnimplementedEventServiceServer()
}

func RegisterEventServiceServer(s grpc.ServiceRegistrar, srv EventServiceServer) {
	s.RegisterService(&EventService_ServiceDesc, srv)
}

func _EventService_ClientConnects_Handler(srv interface{}, ctx context.Context, dec func(interface{}) error, interceptor grpc.UnaryServerInterceptor) (interface{}, error) {
	in := new(ClientConnectsRequest)
	if err := dec(in); err != nil {
		return nil, err
	}
	if interceptor == nil {
		return srv.(EventServiceServer).ClientConnects(ctx, in)
	}
	info := &grpc.UnaryServerInfo{
		Server:     srv,
		FullMethod: EventService_ClientConnects_FullMethodName,
	}
	handler := func(ctx context.Context, req interface{}) (interface{}, error) {
		return srv.(EventServiceServer).ClientConnects(ctx, req.(*ClientConnectsRequest))
	}
	return interceptor(ctx, in, info, handler)
}

func _EventService_ClientSubscribeLocation_Handler(srv interface{}, ctx context.Context, dec func(interface{}) error, interceptor grpc.UnaryServerInterceptor) (interface{}, error) {
	in := new(ClientSubscribeLocationRequest)
	if err := dec(in); err != nil {
		return nil, err
	}
	if interceptor == nil {
		return srv.(EventServiceServer).ClientSubscribeLocation(ctx, in)
	}
	info := &grpc.UnaryServerInfo{
		Server:     srv,
		FullMethod: EventService_ClientSubscribeLocation_FullMethodName,
	}
	handler := func(ctx context.Context, req interface{}) (interface{}, error) {
		return srv.(EventServiceServer).ClientSubscribeLocation(ctx, req.(*ClientSubscribeLocationRequest))
	}
	return interceptor(ctx, in, info, handler)
}

// EventService_ServiceDesc is the grpc.ServiceDesc for EventService service.
// It's only intended for direct use with grpc.RegisterService,
// and not to be introspected or modified (even as a copy)
var EventService_ServiceDesc = grpc.ServiceDesc{
	ServiceName: "event.EventService",
	HandlerType: (*EventServiceServer)(nil),
	Methods: []grpc.MethodDesc{
		{
			MethodName: "ClientConnects",
			Handler:    _EventService_ClientConnects_Handler,
		},
		{
			MethodName: "ClientSubscribeLocation",
			Handler:    _EventService_ClientSubscribeLocation_Handler,
		},
	},
	Streams:  []grpc.StreamDesc{},
	Metadata: "event.proto",
}
