// All necessary includes and defines are here

#include "defparams.hpp"
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
#include "Food.hpp"
#include "StagHuntRobot.hpp"
#include "BestFitEval.hpp"
#include "MeanFitEval.hpp"
#include "BestEverFitEval.hpp"
#include "AllFitEvalStat.hpp"
#include "AllFitBehaviourVideo.hpp"
#include "PhenChasseur.hpp"
#include "ElitistGen.hpp"
#include "FitnessProp.hpp"
#include "Elitist.hpp"
#include "StagHuntEvalParallelPop.hpp"

#include "StopEval.hpp"

using namespace sferes;
using namespace sferes::gen::evo_float;
