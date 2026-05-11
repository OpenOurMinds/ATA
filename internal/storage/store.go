// Package storage provides embedded persistence via BoltDB.
// Replaces all CSV/JSON file dumps with transactional key-value storage.
package storage

import (
	"encoding/json"
	"fmt"

	bolt "go.etcd.io/bbolt"
)

// Standard bucket names.
var (
	BucketSouls     = []byte("souls")
	BucketTasks     = []byte("tasks")
	BucketDecisions = []byte("decisions")
	BucketMetrics   = []byte("metrics")
)

// Store is a BoltDB-backed key-value store.
type Store struct {
	db *bolt.DB
}

// Open opens or creates a BoltDB database at the given path.
func Open(path string) (*Store, error) {
	db, err := bolt.Open(path, 0600, &bolt.Options{})
	if err != nil {
		return nil, fmt.Errorf("open db at %s: %w", path, err)
	}

	// Create default buckets.
	err = db.Update(func(tx *bolt.Tx) error {
		for _, bucket := range [][]byte{BucketSouls, BucketTasks, BucketDecisions, BucketMetrics} {
			if _, err := tx.CreateBucketIfNotExists(bucket); err != nil {
				return fmt.Errorf("create bucket %s: %w", bucket, err)
			}
		}
		return nil
	})
	if err != nil {
		db.Close()
		return nil, err
	}

	return &Store{db: db}, nil
}

// Close closes the database.
func (s *Store) Close() error {
	return s.db.Close()
}

// Put stores a JSON-serializable value under the given bucket and key.
func (s *Store) Put(bucket []byte, key string, value interface{}) error {
	data, err := json.Marshal(value)
	if err != nil {
		return fmt.Errorf("marshal: %w", err)
	}
	return s.db.Update(func(tx *bolt.Tx) error {
		b := tx.Bucket(bucket)
		if b == nil {
			return fmt.Errorf("bucket %s not found", bucket)
		}
		return b.Put([]byte(key), data)
	})
}

// Get retrieves a value by bucket and key, unmarshaling into dst.
func (s *Store) Get(bucket []byte, key string, dst interface{}) error {
	return s.db.View(func(tx *bolt.Tx) error {
		b := tx.Bucket(bucket)
		if b == nil {
			return fmt.Errorf("bucket %s not found", bucket)
		}
		data := b.Get([]byte(key))
		if data == nil {
			return fmt.Errorf("key %q not found", key)
		}
		return json.Unmarshal(data, dst)
	})
}

// Delete removes a key from a bucket.
func (s *Store) Delete(bucket []byte, key string) error {
	return s.db.Update(func(tx *bolt.Tx) error {
		b := tx.Bucket(bucket)
		if b == nil {
			return fmt.Errorf("bucket %s not found", bucket)
		}
		return b.Delete([]byte(key))
	})
}

// Count returns the number of keys in a bucket.
func (s *Store) Count(bucket []byte) (int, error) {
	var count int
	err := s.db.View(func(tx *bolt.Tx) error {
		b := tx.Bucket(bucket)
		if b == nil {
			return fmt.Errorf("bucket %s not found", bucket)
		}
		count = b.Stats().KeyN
		return nil
	})
	return count, err
}

// ForEach iterates over all key-value pairs in a bucket.
func (s *Store) ForEach(bucket []byte, fn func(key string, value []byte) error) error {
	return s.db.View(func(tx *bolt.Tx) error {
		b := tx.Bucket(bucket)
		if b == nil {
			return fmt.Errorf("bucket %s not found", bucket)
		}
		return b.ForEach(func(k, v []byte) error {
			return fn(string(k), v)
		})
	})
}
