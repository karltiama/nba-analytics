import { PrismaClient } from '@prisma/client'

const prisma = new PrismaClient()

async function testConnection() {
  try {
    console.log('🔄 Testing database connection...')
    await prisma.$connect()
    console.log('✅ Database connection successful!')
    
    // Test a simple query
    const teamCount = await prisma.team.count()
    console.log(`📊 Teams in database: ${teamCount}`)
    
    // Test creating a sample team
    const sampleTeam = await prisma.team.create({
      data: {
        name: 'Test Team',
        abbreviation: 'TEST',
        city: 'Test City',
        conference: 'Eastern',
        division: 'Atlantic'
      }
    })
    console.log('✅ Sample team created:', sampleTeam.name)
    
    // Clean up test data
    await prisma.team.delete({
      where: { id: sampleTeam.id }
    })
    console.log('🧹 Test data cleaned up')
    
  } catch (error) {
    console.error('❌ Database connection failed:', error)
    console.error('Please check your DATABASE_URL in .env.local')
  } finally {
    await prisma.$disconnect()
  }
}

testConnection()
