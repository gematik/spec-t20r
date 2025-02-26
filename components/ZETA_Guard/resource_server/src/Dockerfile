# Dockerfile for rs-vsdm2 Go server

# Builder stage: Compile the Go application
FROM golang:1.23.6 AS builder

WORKDIR /app

# Copy go.mod and go.sum to download dependencies
COPY go.mod go.sum ./
RUN go mod download

# Copy the source code
COPY . .

# Build the application
#RUN go build -o rs-vsdm2 ./rs-vsdm2.go
RUN CGO_ENABLED=0 GOOS=linux GOARCH=amd64 go build -o rs-vsdm2 ./rs-vsdm2.go

# Runtime stage: Create a minimal image to run the application
FROM alpine:latest

WORKDIR /app

RUN apk add --no-cache ca-certificates

# Copy the executable from the builder stage
COPY --from=builder /app/rs-vsdm2 /app/rs-vsdm2

# Expose the port the app listens on
EXPOSE 8080

# Command to run the executable
CMD ["./rs-vsdm2"]
