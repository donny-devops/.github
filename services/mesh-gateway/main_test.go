package main

import (
	"bytes"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"
)

func TestHealthAndCatalog(t *testing.T) {
	handler := newMux(defaultCatalog())

	health := httptest.NewRecorder()
	handler.ServeHTTP(health, httptest.NewRequest(http.MethodGet, "/health", nil))
	if health.Code != http.StatusOK {
		t.Fatalf("health: %d", health.Code)
	}

	catalog := httptest.NewRecorder()
	handler.ServeHTTP(catalog, httptest.NewRequest(http.MethodGet, "/v1/catalog", nil))
	if catalog.Code != http.StatusOK {
		t.Fatalf("catalog: %d", catalog.Code)
	}
}

func TestEnvelopeValidation(t *testing.T) {
	handler := newMux(defaultCatalog())
	body, _ := json.Marshal(envelope{Source: "intake", Target: "decision", Intent: "qualify"})
	rec := httptest.NewRecorder()
	handler.ServeHTTP(rec, httptest.NewRequest(http.MethodPost, "/v1/envelopes", bytes.NewReader(body)))
	if rec.Code != http.StatusAccepted {
		t.Fatalf("envelope: %d %s", rec.Code, rec.Body.String())
	}
}
