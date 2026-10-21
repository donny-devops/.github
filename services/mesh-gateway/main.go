package main

import (
	"encoding/json"
	"log"
	"net/http"
	"os"
	"time"
)

type sku struct {
	ID          string  `json:"id"`
	Name        string  `json:"name"`
	PriceUSD    float64 `json:"price_usd"`
	Cadence     string  `json:"cadence"`
	Lane        string  `json:"lane"`
	Description string  `json:"description"`
	Repo        string  `json:"repo"`
}

type envelope struct {
	Source    string         `json:"source"`
	Target    string         `json:"target"`
	Intent    string         `json:"intent"`
	Payload   map[string]any `json:"payload"`
	ID        string         `json:"id,omitempty"`
	TraceID   string         `json:"trace_id,omitempty"`
	CreatedAt string         `json:"created_at,omitempty"`
}

type catalogFile struct {
	SKUs []sku `json:"skus"`
}

func loadCatalog(path string) ([]sku, error) {
	raw, err := os.ReadFile(path)
	if err != nil {
		return defaultCatalog(), nil
	}
	var file catalogFile
	if err := json.Unmarshal(raw, &file); err != nil {
		return nil, err
	}
	return file.SKUs, nil
}

func defaultCatalog() []sku {
	return []sku{{
		ID: "mesh.lane.ping", Name: "Paid agent ping", PriceUSD: 25,
		Cadence: "one_time", Lane: "ping", Description: "Paid inbox ping",
		Repo: "https://github.com/donny-devops/openclaw-revenue-engine",
	}}
}

func newMux(skus []sku) http.Handler {
	mux := http.NewServeMux()
	mux.HandleFunc("/health", func(w http.ResponseWriter, r *http.Request) {
		writeJSON(w, http.StatusOK, map[string]any{"ok": true, "service": "mesh-gateway"})
	})
	mux.HandleFunc("/v1/catalog", func(w http.ResponseWriter, r *http.Request) {
		writeJSON(w, http.StatusOK, map[string]any{"skus": skus})
	})
	mux.HandleFunc("/v1/envelopes", func(w http.ResponseWriter, r *http.Request) {
		if r.Method != http.MethodPost {
			http.Error(w, "method not allowed", http.StatusMethodNotAllowed)
			return
		}
		var env envelope
		if err := json.NewDecoder(r.Body).Decode(&env); err != nil {
			http.Error(w, "invalid envelope", http.StatusBadRequest)
			return
		}
		if env.Source == "" || env.Target == "" || env.Intent == "" {
			http.Error(w, "source, target, and intent are required", http.StatusBadRequest)
			return
		}
		if env.CreatedAt == "" {
			env.CreatedAt = time.Now().UTC().Format(time.RFC3339)
		}
		writeJSON(w, http.StatusAccepted, map[string]any{"accepted": true, "envelope": env})
	})
	return mux
}

func writeJSON(w http.ResponseWriter, status int, payload any) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(status)
	_ = json.NewEncoder(w).Encode(payload)
}

func main() {
	addr := os.Getenv("PIPEFISH_GATEWAY_ADDR")
	if addr == "" {
		addr = "127.0.0.1:8787"
	}
	skus, err := loadCatalog(os.Getenv("PIPEFISH_CATALOG"))
	if err != nil {
		log.Fatal(err)
	}
	log.Printf("mesh-gateway listening on %s", addr)
	log.Fatal(http.ListenAndServe(addr, newMux(skus)))
}
