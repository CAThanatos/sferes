// All necessary includes and defines are here


#include <iostream>
#include <math.h>
#include <ctime>
#include <fstream>
#include <sferes/phen/parameters.hpp>
#include <sferes/ea/nsga2.hpp>
#include <sferes/ea/rank_simple.hpp>
#include <sferes/ea/cmaes.hpp>
#include <sferes/gen/cmaes.hpp>
#include <sferes/eval/eval.hpp>
#include <sferes/stat/pareto_front.hpp>
#include <sferes/modif/dummy.hpp>
#include <sferes/run.hpp>

#include <modules/fastsim_multi2/simu_fastsim_multi.hpp>
#include <modules/nn2/mlp.hpp>

#include "Hunter.hpp"
#include "StagHuntRobot.hpp"
#include "BestFitEval.hpp"
#include "BestLeadershipEval.hpp"
#include "MeanFitEval.hpp"
#include "BestEverFitEval.hpp"
#include "AllFitEvalStat.hpp"
#include "AllLeadershipEvalStat.hpp"
#include "PhenTraveler.hpp"
#include "ElitistGen.hpp"
#include "FitnessProp.hpp"
#include "Elitist.hpp"
#include "StagHuntEvalParallel.hpp"
#include "BestFitBehaviourVideo.hpp"
#include "Waypoint.hpp"

#ifdef COEVO
#include "Elitist-CoEvo.hpp"
#include "StagHuntEvalParallel-CoEvo.hpp"
#include "BestFitEval-CoEvo.hpp"
#include "BestLeadershipEval-CoEvo.hpp"
#include "MeanFitEval-CoEvo.hpp"
#include "BestEverFitEval-CoEvo.hpp"
#include "AllFitEvalStat-CoEvo.hpp"
#include "AllLeadershipEvalStat-CoEvo.hpp"
#include "BestFitBehaviourVideo-CoEvo.hpp"
#endif

#include "StopEval.hpp"

using namespace sferes;
using namespace sferes::gen::evo_float;
