// Simple database connection test
const { Client } = require('pg');

async function testConnection() {
  const client = new Client({
    connectionString: process.env.DATABASE_URL
  });

  try {
    console.log('🔄 Testing direct PostgreSQL connection...');
    await client.connect();
    console.log('✅ PostgreSQL connection successful!');
    
    // Test a simple query
    const result = await client.query('SELECT NOW() as current_time');
    console.log('📊 Current database time:', result.rows[0].current_time);
    
  } catch (error) {
    console.error('❌ PostgreSQL connection failed:', error.message);
    console.error('Error code:', error.code);
  } finally {
    await client.end();
  }
}

testConnection();
