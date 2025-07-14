#!/usr/bin/env python3
"""
EfficacyLens: 临床试验数据收集脚本
直接调用ClinicalTrials.gov API，无需n8n
"""

import requests
import json
import pandas as pd
from datetime import datetime
import time
import os

class TrialCollector:
    def __init__(self):
        self.base_url = "https://clinicaltrials.gov/api/query"
        self.collected_data = []
        
    def search_completed_trials(self, max_trials=50):
        """搜索已完成的III期试验"""
        print("🔍 搜索已完成的III期临床试验...")
        
        params = {
            'expr': 'AREA[StudyType]EXACT["Interventional"] AND AREA[Phase]PHASE3 AND AREA[OverallStatus]EXACT["Completed"] AND AREA[HasResults]EXACT["true"]',
            'fields': 'NCTId,BriefTitle,Condition,InterventionName,PrimaryOutcomeMeasure,SecondaryOutcomeMeasure,CompletionDate,EnrollmentCount,HasResults,ResultsFirstPostDate',
            'min_rnk': '1',
            'max_rnk': str(max_trials),
            'fmt': 'json'
        }
        
        try:
            response = requests.get(f"{self.base_url}/study_fields", params=params)
            response.raise_for_status()
            data = response.json()
            
            studies = data.get('StudyFieldsResponse', {}).get('StudyFields', [])
            print(f"✅ 找到 {len(studies)} 个符合条件的试验")
            return studies
            
        except requests.RequestException as e:
            print(f"❌ API请求失败: {e}")
            return []
    
    def process_trials(self, studies):
        """处理和筛选试验数据"""
        print("📊 处理和筛选试验数据...")
        processed_data = []
        
        for study in studies:
            # 只保留有结果的已完成试验
            if study.get('HasResults') and study['HasResults'][0] == 'true':
                processed_study = {
                    'nctId': study.get('NCTId', [''])[0],
                    'title': study.get('BriefTitle', [''])[0],
                    'condition': '; '.join(study.get('Condition', [])),
                    'intervention': '; '.join(study.get('InterventionName', [])),
                    'primaryOutcome': study.get('PrimaryOutcomeMeasure', [''])[0],
                    'secondaryOutcome': '; '.join(study.get('SecondaryOutcomeMeasure', [])),
                    'completionDate': study.get('CompletionDate', [''])[0],
                    'enrollmentCount': int(study.get('EnrollmentCount', ['0'])[0]) if study.get('EnrollmentCount', ['0'])[0].isdigit() else 0,
                    'resultsPostedDate': study.get('ResultsFirstPostDate', [''])[0],
                    'resultsUrl': f"https://clinicaltrials.gov/study/{study.get('NCTId', [''])[0]}/results",
                    'qualityScore': {
                        'hasResults': bool(study.get('HasResults', [''])[0]),
                        'hasPrimary': bool(study.get('PrimaryOutcomeMeasure', [''])[0]),
                        'hasEnrollment': bool(study.get('EnrollmentCount', [''])[0]),
                        'isLargeTrial': int(study.get('EnrollmentCount', ['0'])[0]) > 100 if study.get('EnrollmentCount', ['0'])[0].isdigit() else False
                    }
                }
                processed_data.append(processed_study)
        
        # 按入组人数排序，优先选择大样本试验
        processed_data.sort(key=lambda x: x['enrollmentCount'], reverse=True)
        
        # 只取前20个
        top_20 = processed_data[:20]
        print(f"🎯 筛选出前20个优质试验 (样本量: {top_20[0]['enrollmentCount']} - {top_20[-1]['enrollmentCount']}人)")
        
        return top_20
    
    def get_detailed_results(self, trial):
        """获取单个试验的详细结果数据"""
        nct_id = trial['nctId']
        print(f"📥 获取 {nct_id} 的详细数据...")
        
        params = {
            'expr': f'AREA[NCTId]{nct_id}',
            'fmt': 'json'
        }
        
        try:
            response = requests.get(f"{self.base_url}/full_studies", params=params)
            response.raise_for_status()
            data = response.json()
            
            study = data.get('FullStudiesResponse', {}).get('FullStudies', [{}])[0].get('Study', {})
            
            if study:
                results_section = study.get('ResultsSection', {})
                protocol_section = study.get('ProtocolSection', {})
                
                detailed_result = {
                    # 基本信息
                    'nctId': protocol_section.get('IdentificationModule', {}).get('NCTId', ''),
                    'title': protocol_section.get('IdentificationModule', {}).get('BriefTitle', ''),
                    
                    # 研究设计
                    'studyType': protocol_section.get('DesignModule', {}).get('StudyType', ''),
                    'phase': ', '.join(protocol_section.get('DesignModule', {}).get('PhaseList', {}).get('Phase', [])),
                    'allocation': protocol_section.get('DesignModule', {}).get('DesignInfo', {}).get('DesignAllocation', ''),
                    'masking': protocol_section.get('DesignModule', {}).get('DesignInfo', {}).get('DesignMasking', ''),
                    
                    # 参与者信息
                    'enrollmentCount': protocol_section.get('DesignModule', {}).get('EnrollmentInfo', {}).get('EnrollmentCount', 0),
                    'eligibilityCriteria': protocol_section.get('EligibilityModule', {}).get('EligibilityCriteria', ''),
                    
                    # 干预措施
                    'interventions': [
                        {
                            'type': i.get('InterventionType', ''),
                            'name': i.get('InterventionName', ''),
                            'description': i.get('InterventionDescription', '')
                        }
                        for i in protocol_section.get('ArmsInterventionsModule', {}).get('InterventionList', {}).get('Intervention', [])
                    ],
                    
                    # 主要结果
                    'primaryOutcomes': [
                        {
                            'measure': o.get('PrimaryOutcomeMeasure', ''),
                            'timeFrame': o.get('PrimaryOutcomeTimeFrame', ''),
                            'description': o.get('PrimaryOutcomeDescription', '')
                        }
                        for o in protocol_section.get('OutcomesModule', {}).get('PrimaryOutcomeList', {}).get('PrimaryOutcome', [])
                    ],
                    
                    # 结果数据 (关键部分)
                    'results': {
                        'participantFlow': results_section.get('ParticipantFlowModule', {}),
                        'baselineCharacteristics': results_section.get('BaselineCharacteristicsModule', {}),
                        'outcomeData': [
                            {
                                'title': outcome.get('OutcomeMeasureTitle', ''),
                                'description': outcome.get('OutcomeMeasureDescription', ''),
                                'timeFrame': outcome.get('OutcomeMeasureTimeFrame', ''),
                                'type': outcome.get('OutcomeMeasureType', ''),
                                'results': [
                                    {
                                        'groupDescription': analysis.get('OutcomeMeasureAnalysisGroupDescription', ''),
                                        'statisticalMethod': analysis.get('OutcomeMeasureAnalysisStatisticalMethod', ''),
                                        'pValue': analysis.get('OutcomeMeasureAnalysisPValue', ''),
                                        'statisticalComment': analysis.get('OutcomeMeasureAnalysisStatisticalComment', '')
                                    }
                                    for analysis in outcome.get('OutcomeMeasureAnalysisList', {}).get('OutcomeMeasureAnalysis', [])
                                ]
                            }
                            for outcome in results_section.get('OutcomeMeasuresModule', {}).get('OutcomeMeasureList', {}).get('OutcomeMeasure', [])
                        ],
                        'adverseEvents': results_section.get('AdverseEventsModule', {})
                    },
                    
                    # 元数据
                    'lastUpdateDate': protocol_section.get('StatusModule', {}).get('LastUpdatePostDate', ''),
                    'resultsFirstPosted': protocol_section.get('StatusModule', {}).get('ResultsFirstPostDate', ''),
                    'collectedAt': datetime.now().isoformat()
                }
                
                return detailed_result
                
        except requests.RequestException as e:
            print(f"❌ 获取 {nct_id} 详细数据失败: {e}")
            return None
    
    def collect_all_data(self, max_trials=50):
        """完整的数据收集流程"""
        print("🚀 开始收集临床试验数据...")
        
        # 1. 搜索试验
        studies = self.search_completed_trials(max_trials)
        if not studies:
            return []
        
        # 2. 处理和筛选
        top_trials = self.process_trials(studies)
        
        # 3. 获取详细结果
        detailed_results = []
        for i, trial in enumerate(top_trials, 1):
            print(f"📊 处理第 {i}/20 个试验...")
            detailed_result = self.get_detailed_results(trial)
            if detailed_result:
                detailed_results.append(detailed_result)
            
            # 避免API限制，添加延迟
            time.sleep(1)
        
        self.collected_data = detailed_results
        print(f"\n🎉 数据收集完成！共收集 {len(detailed_results)} 个详细试验结果")
        
        return detailed_results
    
    def save_to_files(self, output_dir="data"):
        """保存数据到文件"""
        if not self.collected_data:
            print("❌ 没有数据可保存")
            return
        
        # 创建输出目录
        os.makedirs(output_dir, exist_ok=True)
        
        # 保存JSON格式
        json_file = f"{output_dir}/clinical_trials_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(self.collected_data, f, ensure_ascii=False, indent=2)
        
        # 保存CSV格式 (基本信息)
        csv_data = []
        for trial in self.collected_data:
            csv_row = {
                'NCT_ID': trial['nctId'],
                '研究标题': trial['title'],
                '研究类型': trial['studyType'],
                '试验分期': trial['phase'],
                '入组人数': trial['enrollmentCount'],
                '干预措施': ', '.join([i['name'] for i in trial['interventions']]),
                '主要终点': ', '.join([o['measure'] for o in trial['primaryOutcomes']]),
                '结果数据数量': len(trial['results']['outcomeData']),
                '收集时间': trial['collectedAt'],
                '结果链接': f"https://clinicaltrials.gov/study/{trial['nctId']}/results"
            }
            csv_data.append(csv_row)
        
        csv_file = f"{output_dir}/clinical_trials_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        df = pd.DataFrame(csv_data)
        df.to_csv(csv_file, index=False, encoding='utf-8')
        
        print(f"✅ 数据已保存:")
        print(f"   📄 JSON详细数据: {json_file}")
        print(f"   📊 CSV摘要数据: {csv_file}")
        
        # 显示数据摘要
        self.show_summary()
    
    def show_summary(self):
        """显示数据收集摘要"""
        if not self.collected_data:
            return
        
        print(f"\n📊 数据收集摘要:")
        print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print(f"📋 总试验数: {len(self.collected_data)}")
        print(f"👥 平均入组人数: {sum(t['enrollmentCount'] for t in self.collected_data) // len(self.collected_data)}")
        print(f"🔬 包含结果数据的试验: {sum(1 for t in self.collected_data if t['results']['outcomeData'])}")
        
        print(f"\n🏆 前5个大样本试验:")
        for i, trial in enumerate(self.collected_data[:5], 1):
            print(f"  {i}. {trial['nctId']}: {trial['title'][:50]}... ({trial['enrollmentCount']}人)")
        
        print(f"\n🎯 下一步: 开始构建LangChain解析pipeline (第3-5周)")

def main():
    """主函数"""
    print("🔬 EfficacyLens - 临床试验数据收集器")
    print("=" * 50)
    
    collector = TrialCollector()
    
    try:
        # 收集数据
        data = collector.collect_all_data(max_trials=50)
        
        if data:
            # 保存数据
            collector.save_to_files()
            print(f"\n✅ 第1-2周任务完成！已为第3-5周的LangChain开发准备好数据。")
        else:
            print("❌ 数据收集失败")
            
    except KeyboardInterrupt:
        print("\n⏹️ 用户中断了数据收集")
    except Exception as e:
        print(f"❌ 发生错误: {e}")

if __name__ == "__main__":
    main() 