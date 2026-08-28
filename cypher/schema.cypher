// Schema Constraints and Indexes
// This ensures data integrity and improves lookup performance.

CREATE CONSTRAINT IF NOT EXISTS FOR (c:Company) REQUIRE c.id IS UNIQUE;
CREATE CONSTRAINT IF NOT EXISTS FOR (p:Person) REQUIRE p.id IS UNIQUE;
CREATE CONSTRAINT IF NOT EXISTS FOR (proj:Project) REQUIRE proj.id IS UNIQUE;
CREATE CONSTRAINT IF NOT EXISTS FOR (t:Task) REQUIRE t.id IS UNIQUE;
CREATE CONSTRAINT IF NOT EXISTS FOR (m:Meeting) REQUIRE m.id IS UNIQUE;
CREATE CONSTRAINT IF NOT EXISTS FOR (e:Email) REQUIRE e.id IS UNIQUE;

// Indexes for common search fields
CREATE INDEX IF NOT EXISTS FOR (p:Person) ON (p.name);
CREATE INDEX IF NOT EXISTS FOR (p:Person) ON (p.email);
CREATE INDEX IF NOT EXISTS FOR (proj:Project) ON (proj.name);
CREATE INDEX IF NOT EXISTS FOR (proj:Project) ON (proj.status);
CREATE INDEX IF NOT EXISTS FOR (t:Task) ON (t.status);
