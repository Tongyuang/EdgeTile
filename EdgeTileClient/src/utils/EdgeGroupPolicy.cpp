//
// Created by Xu Wang on 2020/4/10.
//

#include "EdgeGroupPolicy.hpp"
#include "../components/EdgeEncoder.hpp"
#include "../include/EdgeClient.hpp"
#include "../utils/Utils.hpp"

using namespace Edge;

EdgeGroupPolicy::EdgeGroupPolicy(){
    encoder = NULL;
}

EdgeGroupPolicy::EdgeGroupPolicy(EdgeEncoder* enc){
    encoder = enc;
}

void EdgeGroupPolicy::default_policy(int tw, int th, EdgeGroupPolicy &policy) {
    policy.groups.clear();
    for(int i = 0; i < th; i++){
        for(int j = 0; j < tw; j++){
            Rect a;
            a.x = j, a.y = i, a.width = 1, a.height = 1;
            policy.groups.push_back(a);
        }
    }
    // int left_tw = tw / 2;
    // int right_tw = tw - left_tw;
    // int top_th = th / 2;
    // int bottom_th = th - top_th;
    
    // Rect a;
    // a.x = 0, a.y = 0, a.width = left_tw, a.height = top_th;
    // Rect b;
    // b.x = left_tw, b.y = 0, b.width = right_tw, b.height = top_th;
    // Rect c;
    // c.x = 0, c.y = top_th, c.width = left_tw, c.height = bottom_th;
    // Rect d;
    // d.x = left_tw, d.y = top_th, d.width = right_tw, d.height = bottom_th;
    // policy.groups.push_back(d);
    // policy.groups.push_back(a);
    // policy.groups.push_back(c);
    // policy.groups.push_back(b);
//    policy.groups.push_back(d);
//    policy.groups.push_back(b);
//    policy.groups.push_back(c);
//    policy.groups.push_back(a);

}
EdgeGroupPolicy EdgeGroupPolicy::dynamic_by_object_nums(int frame_id, vector<int> upload_order) {
    groups.clear();
    for(int i = 0; i < this->encoder->tile_height; i++){
        for(int j = 0; j <  this->encoder->tile_width; j++){
            Rect a;
            a.x = j, a.y = i, a.width = 1, a.height = 1;
            groups.push_back(a);
        }
    }
    EdgeGroupPolicy new_policy(this->encoder);
    // printf("%d:", frame_id);
    for(int i = 0; i < upload_order.size(); i++){
        // printf("%d", upload_order[i]);
        new_policy.groups.push_back(groups[upload_order[i]]);
        // int tid = new_policy.groups[i].y * this->encoder->tile_width + new_policy.groups[i].x;
        // printf("[%d] ", tid);
    }
    // printf("\n");
    return new_policy;
}

void EdgeGroupPolicy::one_group_policy(int tw, int th, EdgeGroupPolicy &policy) {
    policy.groups.clear();
    Rect a;
    a.x = 0, a.y = 0, a.width = tw, a.height = th;
    policy.groups.push_back(a);
}

EdgeGroupPolicy EdgeGroupPolicy::dynamic_by_count() {
   EdgeClient* client = (EdgeClient*)encoder->app;
   auto frames = client->get_framePool()->frames;
   int frame_count = frames.size();
   vector<Rect> groupBoxes;
   vector<int> group_count;
   for(int i = 0; i < groups.size(); i ++){
       groupBoxes.push_back(group2box(i));
       group_count.push_back(0);
   }
   for(int i = frame_count - 1; i>=0; i --){
       shared_ptr<EdgeFrame> f = frames[i];
       if(f->is_track_finished){
           for(auto box : f->client_bboxes){
               vector<double> iou;
               for(int j = 0; j < groupBoxes.size(); j ++) {
                   iou.push_back(box.intersectRectPercentage(groupBoxes[j]));
               }
               group_count[distance(iou.begin(), max_element(iou.begin(), iou.end()))] ++;
           }
           auto sort_idx = Utils::sort_indexes(group_count);
           EdgeGroupPolicy new_policy(this->encoder);
           for(int i = sort_idx.size() - 1; i >=0; i --){
                new_policy.groups.push_back(groups[sort_idx[i]]);
           }
           return new_policy;
           //this->groups.clear();
           //this->groups.insert(this->groups.begin(),new_groups.begin(), new_groups.end());
       }
   }
   return *this;
}



Rect EdgeGroupPolicy::group2box(int group_id) {
    Rect groupRect = groups[group_id];
    Rect groupBox;
    int first_tile = groupRect.x + groupRect.y * encoder->tile_width;
    int last_tile = groupRect.x + groupRect.width - 1  + (groupRect.y + groupRect.height -1) * encoder->tile_width;
    groupBox.x = encoder->tiles_position[first_tile].x;
    groupBox.y = encoder->tiles_position[first_tile].y;
    int xmax = encoder->tiles_position[last_tile].x + encoder->tiles_position[last_tile].width;
    int ymax = encoder->tiles_position[last_tile].y + encoder->tiles_position[last_tile].height;
    groupBox.width = xmax - groupBox.x;
    groupBox.height = ymax - groupBox.y;
    return groupBox;
}

string EdgeGroupPolicy::toString() {
    std::ostringstream os;
    for(int i = 0; i < groups.size(); i ++){
        auto box = groups[i];
        if(i < groups.size() -1) {
            os << box.x << "," << box.y << "," << box.width << ","<<box.height<<",";
        }
        else{
            os << box.x << "," << box.y << "," << box.width << ","<<box.height;
        }
    }
    return os.str();
}

vector<TileMeta> EdgeGroupPolicy::getTileEncodingOrder(int tw, int th) {
    vector<TileMeta> orders;
    for(int i = 0; i < groups.size(); i ++){
        for(int j =0; j < groups[i].width; j ++){
            for(int k = 0; k < groups[i].height; k ++){
                int tid = (k + groups[i].y) * tw + (j + groups[i].x);
                TileMeta m;
                // printf("*%d,",tid);
                m.tile_id = tid;
                m.group_id = i;
                m.group_width = groups[i].width;
                m.group_height = groups[i].height;
                orders.push_back(m);
            }
        }
    }
    // printf("\n");
    return orders;
}
