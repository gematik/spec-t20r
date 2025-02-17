# Dockerfile for rs_vsdm2 Go server

# Builder stage: Compile the Go application
FROM golang:1.22-alpine AS builder

WORKDIR /app

# Copy go.mod and go.sum to download dependencies
COPY go.mod go.sum ./
RUN go mod download

# Copy the source code
COPY . .

# Build the application
RUN go build -o rs_vsdm2 ./rs_vsdm2.go

# Runtime stage: Create a minimal image to run the application
FROM alpine:latest

WORKDIR /app

# Copy the executable from the builder stage
COPY --from=builder /app/rs_vsdm2 /app/rs_vsdm2

# Expose the port the app listens on
EXPOSE 8080

# Command to run the executable
CMD ["./rs_vsdm2"]