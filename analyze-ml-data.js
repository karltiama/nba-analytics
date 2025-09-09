const { PrismaClient } = require('@prisma/client');

const prisma = new PrismaClient();

async function analyzeMLData() {
  console.log('🔍 Analyzing data for ML model development...\n');
  
  try {
    // 1. Overall data statistics
    console.log('=== OVERALL DATA STATISTICS ===');
    const totalGames = await prisma.game.count();
    const gamesWithBetting = await prisma.game.count({
      where: { spread: { not: null } }
    });
    
    console.log(`Total games: ${totalGames.toLocaleString()}`);
    console.log(`Games with betting data: ${gamesWithBetting.toLocaleString()}`);
    console.log(`Coverage: ${((gamesWithBetting / totalGames) * 100).toFixed(1)}%`);
    
    // 2. Target variables analysis
    console.log('\n=== TARGET VARIABLES ANALYSIS ===');
    
    // Point spread analysis
    const spreadStats = await prisma.game.aggregate({
      where: { spread: { not: null } },
      _count: { spread: true },
      _min: { spread: true },
      _max: { spread: true },
      _avg: { spread: true }
    });
    
    console.log('Point Spread:');
    console.log(`  Count: ${spreadStats._count.spread.toLocaleString()}`);
    console.log(`  Min: ${spreadStats._min.spread}`);
    console.log(`  Max: ${spreadStats._max.spread}`);
    console.log(`  Average: ${spreadStats._avg.spread?.toFixed(2)}`);
    
    // Total points analysis
    const totalStats = await prisma.game.aggregate({
      where: { total: { not: null } },
      _count: { total: true },
      _min: { total: true },
      _max: { total: true },
      _avg: { total: true }
    });
    
    console.log('\nTotal Points:');
    console.log(`  Count: ${totalStats._count.total.toLocaleString()}`);
    console.log(`  Min: ${totalStats._min.total}`);
    console.log(`  Max: ${totalStats._max.total}`);
    console.log(`  Average: ${totalStats._avg.total?.toFixed(2)}`);
    
    // Moneyline analysis
    const moneylineStats = await prisma.game.aggregate({
      where: { 
        moneylineHome: { not: null },
        moneylineAway: { not: null }
      },
      _count: { moneylineHome: true },
      _min: { moneylineHome: true },
      _max: { moneylineHome: true },
      _avg: { moneylineHome: true }
    });
    
    console.log('\nMoneyline (Home):');
    console.log(`  Count: ${moneylineStats._count.moneylineHome.toLocaleString()}`);
    console.log(`  Min: ${moneylineStats._min.moneylineHome}`);
    console.log(`  Max: ${moneylineStats._max.moneylineHome}`);
    console.log(`  Average: ${moneylineStats._avg.moneylineHome?.toFixed(2)}`);
    
    // 3. Outcome analysis
    console.log('\n=== OUTCOME ANALYSIS ===');
    
    // Spread outcomes
    const spreadOutcomes = await prisma.game.groupBy({
      by: ['idSpread'],
      where: { idSpread: { not: null } },
      _count: { idSpread: true }
    });
    
    console.log('Spread Outcomes:');
    spreadOutcomes.forEach(outcome => {
      const label = outcome.idSpread === 1 ? 'Favorite Covered' : 
                   outcome.idSpread === 0 ? 'Underdog Covered' : 'Push';
      const percentage = ((outcome._count.idSpread / spreadOutcomes.reduce((sum, o) => sum + o._count.idSpread, 0)) * 100).toFixed(1);
      console.log(`  ${label}: ${outcome._count.idSpread.toLocaleString()} (${percentage}%)`);
    });
    
    // Total outcomes
    const totalOutcomes = await prisma.game.groupBy({
      by: ['idTotal'],
      where: { idTotal: { not: null } },
      _count: { idTotal: true }
    });
    
    console.log('\nTotal Outcomes:');
    totalOutcomes.forEach(outcome => {
      const label = outcome.idTotal === 1 ? 'Over' : 
                   outcome.idTotal === 0 ? 'Under' : 'Push';
      const percentage = ((outcome._count.idTotal / totalOutcomes.reduce((sum, o) => sum + o._count.idTotal, 0)) * 100).toFixed(1);
      console.log(`  ${label}: ${outcome._count.idTotal.toLocaleString()} (${percentage}%)`);
    });
    
    // 4. Feature analysis
    console.log('\n=== FEATURE ANALYSIS ===');
    
    // Season distribution
    const seasonDist = await prisma.game.groupBy({
      by: ['season'],
      where: { spread: { not: null } },
      _count: { season: true },
      orderBy: { season: 'desc' }
    });
    
    console.log('Games by Season:');
    seasonDist.forEach(season => {
      console.log(`  ${season.season}: ${season._count.season.toLocaleString()}`);
    });
    
    // Regular vs Playoffs
    const gameTypeDist = await prisma.game.groupBy({
      by: ['seasonType'],
      where: { spread: { not: null } },
      _count: { seasonType: true }
    });
    
    console.log('\nGame Types:');
    gameTypeDist.forEach(type => {
      const percentage = ((type._count.seasonType / gameTypeDist.reduce((sum, t) => sum + t._count.seasonType, 0)) * 100).toFixed(1);
      console.log(`  ${type.seasonType}: ${type._count.seasonType.toLocaleString()} (${percentage}%)`);
    });
    
    // 5. Data quality check
    console.log('\n=== DATA QUALITY CHECK ===');
    
    const missingSpread = await prisma.game.count({
      where: { spread: null }
    });
    
    const missingTotal = await prisma.game.count({
      where: { total: null }
    });
    
    const missingMoneyline = await prisma.game.count({
      where: { 
        OR: [
          { moneylineHome: null },
          { moneylineAway: null }
        ]
      }
    });
    
    console.log(`Missing spread data: ${missingSpread.toLocaleString()}`);
    console.log(`Missing total data: ${missingTotal.toLocaleString()}`);
    console.log(`Missing moneyline data: ${missingMoneyline.toLocaleString()}`);
    
    // 6. ML Model Recommendations
    console.log('\n=== ML MODEL RECOMMENDATIONS ===');
    console.log('Based on the data analysis:');
    console.log('1. Point Spread Prediction: Binary classification (favorite covers vs underdog covers)');
    console.log('2. Total Points Prediction: Binary classification (over vs under)');
    console.log('3. Game Winner Prediction: Binary classification (home wins vs away wins)');
    console.log('4. Regression Models: Predict actual spread and total values');
    console.log('\nRecommended features to engineer:');
    console.log('- Team performance metrics (win rate, points per game, etc.)');
    console.log('- Head-to-head records');
    console.log('- Recent form (last 5-10 games)');
    console.log('- Home/away performance');
    console.log('- Rest days between games');
    console.log('- Season progression (early vs late season)');
    
  } catch (error) {
    console.error('❌ Analysis failed:', error.message);
  } finally {
    await prisma.$disconnect();
  }
}

// Run the analysis
analyzeMLData()
  .then(() => {
    console.log('\n🎉 Data analysis completed!');
    process.exit(0);
  })
  .catch((error) => {
    console.error('❌ Analysis failed:', error);
    process.exit(1);
  });
