#include <iostream>
#include "linear_camera.hpp"


namespace fastsim
{
//   void LinearCamera :: update(const Posture& pos,
//                              const boost::shared_ptr<Map>& map)
//   {
// #ifdef SYMETRIE_CAMERA
//     float inc = _angular_range / (_pixels.size() - 1);
// #else
//     float inc = _angular_range / _pixels.size();
// #endif

//     float x1 = pos.x();
//     float y1 = pos.y();

//     float r = -_angular_range / 2.0f;
//     for (size_t i = 0; i < _pixels.size(); ++i, r += inc)
//     {
//       assert(i < _pixels.size());

//       _dist[i] = -1.0f;
//       _pixels[i] = -1.0f;

//       float alpha = r + pos.theta();
//       float xr = cos(alpha) * _range + pos.x();
//       float yr = sin(alpha) * _range + pos.x();

//       for (size_t j = 0; j < map->get_illuminated_switches().size(); ++j)
//       {
//         Map::ill_sw_t isv = map->get_illuminated_switches()[j];

//         if(isv->get_on())
//         {
//           float x_isv = isv->get_x();
//           float y_isv = isv->get_y();
//           float r_isv = isv->get_radius();

//           float dist = sqrtf((x_isv - x1) * (x_isv - x1) + (y_isv - y1) * (y_isv - y1));

//           if(dist <= _range)
//           {
//             if((_dist[i] < 0.0f) || (dist < _dist[i]))
//             {
//               if(map->check_inter_ray_circle(x1, y1, xr, yr, x_isv, y_isv, r_isv))
//               {
//                 _pixels[i] = isv->get_color();
//                 _dist[i] = dist;
//               }
//             }
//           }
//         }
//       }
//     }
//   }
  
  void LinearCamera :: update(const Posture& pos,
                             const boost::shared_ptr<Map>& map)
  {
#ifdef SYMETRIE_CAMERA
    float inc = _angular_range / (_pixels.size() - 1);
#else
    float inc = _angular_range / _pixels.size();
#endif

    for(size_t i = 0; i < _pixels.size(); ++i)
    {
      _dist[i] = -1.0f;
      _pixels[i] = -1.0f;
    }

    float x1 = pos.x();
    float y1 = pos.y();
    for (size_t i = 0; i < map->get_illuminated_switches().size(); ++i)
    {
      Map::ill_sw_t isv = map->get_illuminated_switches()[i];

      if(isv->get_on())
      {
        float x_isv = isv->get_x();
        float y_isv = isv->get_y();
        float r = isv->get_radius();

        float dist = sqrtf((x_isv - x1) * (x_isv - x1) + (y_isv - y1) * (y_isv - y1));

        if(dist <= _range)
        {
          // float ang = normalize_angle(atan2(y_isv - y1, x_isv - x1));
          float ang = normalize_angle(asin((y_isv - y1)/dist));

          if(x1 >= x_isv)
          {
            if(y1 >= y_isv)
              ang = -M_PI/2 - (M_PI/2 + ang);
            else
              ang = M_PI/2 + (M_PI/2 - ang);
          }

          // To optimize execution speed, we don't consider iw which are
          // behind the robot
          float dAngle = normalize_angle(pos.theta() - ang);
          if(fabs(dAngle) > M_PI/2)
            continue;

          float x_isv2 = x_isv + cosf(normalize_angle(ang + M_PI/2)) * r;
          float y_isv2 = y_isv + sinf(normalize_angle(ang + M_PI/2)) * r;
          // float limAng1 = normalize_angle(atan2(y_isv2 - y1, x_isv2 - x1));
          float dist2 = sqrtf((x_isv2 - x1) * (x_isv2 - x1) + (y_isv2 - y1) * (y_isv2 - y1));
          float limAng1 = normalize_angle(asin((y_isv2 - y1)/dist2));

          if(x1 >= x_isv2)
          {
            if(y1 >= y_isv2)
              limAng1 = -M_PI/2 - (M_PI/2 + limAng1);
            else
              limAng1 = M_PI/2 + (M_PI/2 - limAng1);
          }

          float limAng2 = normalize_angle(ang - (limAng1 - ang));
          // float x_isv3 = x_isv + cosf(normalize_angle(ang - M_PI/2)) * r;
          // float y_isv3 = y_isv + sinf(normalize_angle(ang - M_PI/2)) * r;
          // float limAng2 = normalize_angle(atan2(y_isv3 - y1, x_isv3 - x1));
          // float limAng2 = 0.0f;
    
          float r = -_angular_range / 2.0f;
          for (size_t j = 0; j < _pixels.size(); ++j, r += inc)
          {
            assert(j < _pixels.size());

            if((_dist[j] < 0.0f) || (dist < _dist[j]))
            {
              float angle = normalize_angle(r + pos.theta());

              if(limAng2 < limAng1)
              {
                if(angle >= limAng2 && angle <= limAng1)
                {
                  _pixels[j] = isv->get_color();
                  _dist[j] = dist;
                }
              }
              else
              {
                if((angle >= limAng2 && angle <= M_PI) || (angle <= limAng1 && angle >= -M_PI))
                {
                  _pixels[j] = isv->get_color();
                  _dist[j] = dist;
                }
              }
            }
          }
        }
      }
    }
  }
}
