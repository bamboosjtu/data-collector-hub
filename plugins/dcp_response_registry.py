from __future__ import annotations

SAMPLE_FILE_COUNT = 66
API_SAMPLE_COUNT = 105

DCP_RESPONSE_API_REGISTRY = [
    {
        "api_name": "owner_dept_list",
        "api_path": "/apit/ebuild2-domain-project-form/v1/ownerDept/queryDeptListAPP",
        "dataset_key": "dataset_d32cb9ff",
        "has_record_schema": true,
        "page_name": "业主项目部",
        "record_schema_count": 1,
        "sample_file": "sample_业主项目部.json",
        "success_sample": true
    },
    {
        "api_name": "owner_dept_personnel",
        "api_path": "/apit/ebuild2-domain-project-form/v1/ownerPerson/queryDeptPerson",
        "dataset_key": "dataset_d32cb9ff",
        "has_record_schema": true,
        "page_name": "业主项目部",
        "record_schema_count": 1,
        "sample_file": "sample_业主项目部.json",
        "success_sample": true
    },
    {
        "api_name": "queryDeptFile",
        "api_path": "/apit/ebuild2-domain-project-form/v1/ownerDept/queryDeptFile",
        "dataset_key": "dataset_d32cb9ff",
        "has_record_schema": true,
        "page_name": "业主项目部",
        "record_schema_count": 1,
        "sample_file": "sample_业主项目部.json",
        "success_sample": true
    },
    {
        "api_name": "queryOwnerDeptProject",
        "api_path": "/apit/ebuild2-domain-project-form/v1/ownerProject/queryOwnerDeptProject",
        "dataset_key": "dataset_d32cb9ff",
        "has_record_schema": true,
        "page_name": "业主项目部",
        "record_schema_count": 2,
        "sample_file": "sample_业主项目部.json",
        "success_sample": true
    },
    {
        "api_name": "queryAllEquipTypeName",
        "api_path": "/apit/ebuild2-domain-quality-accept/v1/mainDevice/queryAllEquipTypeName",
        "dataset_key": "dataset_acc32ade",
        "has_record_schema": true,
        "page_name": "主设备清单维护",
        "record_schema_count": 1,
        "sample_file": "sample_主设备清单维护.json",
        "success_sample": true
    },
    {
        "api_name": "worksite_substation",
        "api_path": "/apit/ebuild2-domain-security-risk/v1/worksite/querySubstationPage",
        "dataset_key": "dataset_5f5a4fcf",
        "has_record_schema": true,
        "page_name": "作业部位管理",
        "record_schema_count": 2,
        "sample_file": "sample_作业部位管理.json",
        "success_sample": true
    },
    {
        "api_name": "worksite_tower",
        "api_path": "/apit/ebuild2-domain-security-risk/v1/worksite/queryTowerPage",
        "dataset_key": "dataset_5f5a4fcf",
        "has_record_schema": true,
        "page_name": "作业部位管理",
        "record_schema_count": 1,
        "sample_file": "sample_作业部位管理.json",
        "success_sample": true
    },
    {
        "api_name": "blackout_execution",
        "api_path": "/apit/ebuild2-domain-plan-foundation/v1/blackoutPlanExecution/queryBlackoutExecutionPage",
        "dataset_key": "dataset_7abd177c",
        "has_record_schema": true,
        "page_name": "停电计划执行上报与查看",
        "record_schema_count": 2,
        "sample_file": "sample_停电计划执行上报与查看.json",
        "success_sample": true
    },
    {
        "api_name": "blackout_execution_details",
        "api_path": "/apit/ebuild2-domain-plan-foundation/v1/blackoutPlanExecution/queryBlackoutExecutionDetails",
        "dataset_key": "dataset_7abd177c",
        "has_record_schema": true,
        "page_name": "停电计划执行上报与查看",
        "record_schema_count": 1,
        "sample_file": "sample_停电计划执行上报与查看.json",
        "success_sample": true
    },
    {
        "api_name": "section_single_projects",
        "api_path": "/apit/ebuild2-common-project-digitization/section/getSingleProject",
        "dataset_key": "dataset_18d113ac",
        "has_record_schema": true,
        "page_name": "区段划分",
        "record_schema_count": 2,
        "sample_file": "sample_区段划分.json",
        "success_sample": true
    },
    {
        "api_name": "section_details",
        "api_path": "/apit/ebuild2-common-project-digitization/section/getSectionInfo",
        "dataset_key": "dataset_18d113ac",
        "has_record_schema": false,
        "page_name": "区段划分",
        "record_schema_count": 0,
        "sample_file": "sample_区段划分.json",
        "success_sample": false
    },
    {
        "api_name": "single_project_maintenance",
        "api_path": "/apit/ebuild2-domain-project-form/v1/sinDivide/queryProjectList",
        "dataset_key": "dataset_814e0a01",
        "has_record_schema": true,
        "page_name": "单项信息维护",
        "record_schema_count": 1,
        "sample_file": "sample_单项信息维护.json",
        "success_sample": true
    },
    {
        "api_name": "substation_single_projects",
        "api_path": "/apit/ebuild2-domain-project-stage/v1/substationCoordinates/querySubSinPrjInfo",
        "dataset_key": "dataset_9d439395",
        "has_record_schema": true,
        "page_name": "变电站坐标",
        "record_schema_count": 1,
        "sample_file": "sample_变电站坐标.json",
        "success_sample": true
    },
    {
        "api_name": "substation_coordinates",
        "api_path": "/apit/ebuild2-domain-project-stage/v1/substationCoordinates/querySubstationCoordinates",
        "dataset_key": "dataset_9d439395",
        "has_record_schema": false,
        "page_name": "变电站坐标",
        "record_schema_count": 0,
        "sample_file": "sample_变电站坐标.json",
        "success_sample": true
    },
    {
        "api_name": "querySubstationCoordinatesAmbitus",
        "api_path": "/apit/ebuild2-domain-project-stage/v1/substationCoordinates/querySubstationCoordinatesAmbitus",
        "dataset_key": "dataset_9d439395",
        "has_record_schema": false,
        "page_name": "变电站坐标",
        "record_schema_count": 0,
        "sample_file": "sample_变电站坐标.json",
        "success_sample": true
    },
    {
        "api_name": "querySubstationCoordinatesRelaLineList",
        "api_path": "/apit/ebuild2-domain-project-stage/v1/substationCoordinates/querySubstationCoordinatesRelaLineList",
        "dataset_key": "dataset_9d439395",
        "has_record_schema": false,
        "page_name": "变电站坐标",
        "record_schema_count": 0,
        "sample_file": "sample_变电站坐标.json",
        "success_sample": true
    },
    {
        "api_name": "production_startup_info",
        "api_path": "/apit/ebuild2-domain-project-stage/v1/production/getPrivateProduction",
        "dataset_key": "dataset_2d518fa0",
        "has_record_schema": true,
        "page_name": "启动投运",
        "record_schema_count": 3,
        "sample_file": "sample_启动投运.json",
        "success_sample": true
    },
    {
        "api_name": "startup_committee",
        "api_path": "/apit/ebuild2-domain-project-stage/v1/openingCommittee/getOpeningCommittee",
        "dataset_key": "dataset_eaa452c4",
        "has_record_schema": true,
        "page_name": "启委会管理",
        "record_schema_count": 4,
        "sample_file": "sample_启委会管理.json",
        "success_sample": true
    },
    {
        "api_name": "weekly_plan",
        "api_path": "/apit/ebuild2-domain-security-risk/v1/weekly/queryWeeklyList",
        "dataset_key": "dataset_9cea6566",
        "has_record_schema": true,
        "page_name": "周计划",
        "record_schema_count": 1,
        "sample_file": "sample_周计划.json",
        "success_sample": true
    },
    {
        "api_name": "countWeeklyList",
        "api_path": "/apit/ebuild2-domain-security-risk/v1/weekly/countWeeklyList",
        "dataset_key": "dataset_9cea6566",
        "has_record_schema": true,
        "page_name": "周计划",
        "record_schema_count": 1,
        "sample_file": "sample_周计划.json",
        "success_sample": true
    },
    {
        "api_name": "weekly_plan_ledger",
        "api_path": "/apit/ebuild2-domain-security-risk/v1/weekly/queryPage",
        "dataset_key": "dataset_303fb5ea",
        "has_record_schema": true,
        "page_name": "周计划一本账",
        "record_schema_count": 1,
        "sample_file": "sample_周计划一本账.json",
        "success_sample": true
    },
    {
        "api_name": "project_rework",
        "api_path": "/apit/ebuild2-agg-frame-project/build/returnOrderPageList",
        "dataset_key": "dataset_520e34d1",
        "has_record_schema": true,
        "page_name": "工程复工",
        "record_schema_count": 1,
        "sample_file": "sample_工程复工.json",
        "success_sample": true
    },
    {
        "api_name": "project_construction_progress",
        "api_path": "/apit/ebuild2-domain-project-stage/v1/prjScheduling/queryPrjList",
        "dataset_key": "dataset_e40827dc",
        "has_record_schema": true,
        "page_name": "工程建设管理",
        "record_schema_count": 3,
        "sample_file": "sample_工程建设管理.json",
        "success_sample": true
    },
    {
        "api_name": "project_management_outline",
        "api_path": "/apit/ebuild2-domain-project-stage/v1/conOutline/queryOutlinePage",
        "dataset_key": "dataset_09285810",
        "has_record_schema": true,
        "page_name": "工程建设管理纲要",
        "record_schema_count": 2,
        "sample_file": "sample_工程建设管理纲要.json",
        "success_sample": true
    },
    {
        "api_name": "commencement_order_create_form",
        "api_path": "/apit/ebuild2-domain-project-stage/v1/commenOrder/createDS",
        "dataset_key": "dataset_22049cc1",
        "has_record_schema": true,
        "page_name": "工程开工令",
        "record_schema_count": 2,
        "sample_file": "sample_工程开工令.json",
        "success_sample": true
    },
    {
        "api_name": "project_summary",
        "api_path": "/apit/ebuild2-domain-project-stage/v1/engineerSummary/getPageResult",
        "dataset_key": "dataset_8c420f1b",
        "has_record_schema": true,
        "page_name": "工程总结汇总",
        "record_schema_count": 1,
        "sample_file": "sample_工程总结汇总.json",
        "success_sample": true
    },
    {
        "api_name": "getSingleProjectInfo",
        "api_path": "/apit/ebuild2-domain-project-stage/v1/engineerSummary/getSingleProjectInfo",
        "dataset_key": "dataset_8c420f1b",
        "has_record_schema": true,
        "page_name": "工程总结汇总",
        "record_schema_count": 1,
        "sample_file": "sample_工程总结汇总.json",
        "success_sample": true
    },
    {
        "api_name": "project_pause",
        "api_path": "/apit/ebuild2-agg-frame-project/build/pageQueryBuildPauseOrder",
        "dataset_key": "dataset_989b3acc",
        "has_record_schema": true,
        "page_name": "工程暂停令",
        "record_schema_count": 1,
        "sample_file": "sample_工程暂停令.json",
        "success_sample": true
    },
    {
        "api_name": "yearly_blackout_plan",
        "api_path": "/apit/ebuild2-domain-plan-foundation/v1/yearBlackoutPlanLookAndSend/getYearBlackoutPlan",
        "dataset_key": "dataset_23a6ebab",
        "has_record_schema": true,
        "page_name": "年度停电计划查看",
        "record_schema_count": 1,
        "sample_file": "sample_年度停电计划查看.json",
        "success_sample": true
    },
    {
        "api_name": "yearly_blackout_plan",
        "api_path": "/apit/ebuild2-domain-plan-foundation/v1/yearBlackoutPlanLookAndSend/getYearBlackoutPlan",
        "dataset_key": "dataset_3a3f9598",
        "has_record_schema": true,
        "page_name": "年度停电计划编制",
        "record_schema_count": 1,
        "sample_file": "sample_年度停电计划编制.json",
        "success_sample": true
    },
    {
        "api_name": "yearly_progress_analysis",
        "api_path": "/apit/ebuild2-domain-plan-progress/v1/provincePlanView/queryBeforeAfterDetail",
        "dataset_key": "dataset_b648af56",
        "has_record_schema": true,
        "page_name": "年度进度计划分析",
        "record_schema_count": 3,
        "sample_file": "sample_年度进度计划分析.json",
        "success_sample": true
    },
    {
        "api_name": "queryBuildDetail",
        "api_path": "/apit/ebuild2-domain-plan-progress/v1/provinceProcess/queryBuildDetail",
        "dataset_key": "dataset_456bbe0b",
        "has_record_schema": true,
        "page_name": "年度进度计划编制",
        "record_schema_count": 2,
        "sample_file": "sample_年度进度计划编制.json",
        "success_sample": true
    },
    {
        "api_name": "commencement_report_create_form",
        "api_path": "/apit/ebuild2-domain-project-stage/v1/commenAppInfo/createDS",
        "dataset_key": "dataset_8975c58e",
        "has_record_schema": true,
        "page_name": "开工报审",
        "record_schema_count": 1,
        "sample_file": "sample_开工报审.json",
        "success_sample": true
    },
    {
        "api_name": "getDrawProcessPicForApp",
        "api_path": "/apit/ebuild2-agg-frame-workbench/v1/worktask/getDrawProcessPicForApp",
        "dataset_key": "dataset_8975c58e",
        "has_record_schema": true,
        "page_name": "开工报审",
        "record_schema_count": 4,
        "sample_file": "sample_开工报审.json",
        "success_sample": true
    },
    {
        "api_name": "queryOpenBoxList",
        "api_path": "/apit/ebuild2-domain-quality-manage/v1/openbox/queryOpenBoxList",
        "dataset_key": "dataset_5b001855",
        "has_record_schema": false,
        "page_name": "开箱检查记录",
        "record_schema_count": 0,
        "sample_file": "sample_开箱检查记录.json",
        "success_sample": true
    },
    {
        "api_name": "technical_scheme_list",
        "api_path": "/apit/ebuild2-domain-security-risk/v1/mainTechnicalScheme/queryMainTechnicalSchemePage",
        "dataset_key": "dataset_9c627a89",
        "has_record_schema": true,
        "page_name": "技术方案一览表",
        "record_schema_count": 1,
        "sample_file": "sample_技术方案一览表.json",
        "success_sample": true
    },
    {
        "api_name": "queryConstructionDeptList",
        "api_path": "/apit/ebuild2-domain-project-form/v1/constructionPersonnelChange/queryConstructionDeptList",
        "dataset_key": "dataset_7dd4ed20",
        "has_record_schema": true,
        "page_name": "施工人员管理",
        "record_schema_count": 1,
        "sample_file": "sample_施工人员管理.json",
        "success_sample": true
    },
    {
        "api_name": "queryConstrPersonnelRecList",
        "api_path": "/apit/ebuild2-domain-project-form/v1/constructionPersonnelChange/queryConstrPersonnelRecList",
        "dataset_key": "dataset_7dd4ed20",
        "has_record_schema": false,
        "page_name": "施工人员管理",
        "record_schema_count": 0,
        "sample_file": "sample_施工人员管理.json",
        "success_sample": true
    },
    {
        "api_name": "work_ticket",
        "api_path": "/apit/ebuild2-domain-security-work/v1/constrWorkTicket/queryConstrWorkTicketPagePc",
        "dataset_key": "dataset_b3dfb2d5",
        "has_record_schema": true,
        "page_name": "施工作业票",
        "record_schema_count": 3,
        "sample_file": "sample_施工作业票.json",
        "success_sample": true
    },
    {
        "api_name": "countTicketNumPc",
        "api_path": "/apit/ebuild2-domain-security-work/v1/constrWorkTicket/countTicketNumPc",
        "dataset_key": "dataset_b3dfb2d5",
        "has_record_schema": true,
        "page_name": "施工作业票",
        "record_schema_count": 1,
        "sample_file": "sample_施工作业票.json",
        "success_sample": true
    },
    {
        "api_name": "construction_tender_contract",
        "api_path": "/apit/ebuild2-domain-plan-foundation/v1/supervisorTenderingContract/getPageResult",
        "dataset_key": "dataset_2b1d6d14",
        "has_record_schema": true,
        "page_name": "施工招投标及合同",
        "record_schema_count": 1,
        "sample_file": "sample_施工招投标及合同.json",
        "success_sample": true
    },
    {
        "api_name": "queryConstructionDeptList",
        "api_path": "/apit/ebuild2-domain-project-form/v1/constructionPersonnelChange/queryConstructionDeptList",
        "dataset_key": "dataset_f680e1a3",
        "has_record_schema": true,
        "page_name": "施工资格报审",
        "record_schema_count": 1,
        "sample_file": "sample_施工资格报审.json",
        "success_sample": true
    },
    {
        "api_name": "page",
        "api_path": "/apit/ebuild2-domain-quality-accept/v1/divide/page",
        "dataset_key": "dataset_f028b089",
        "has_record_schema": true,
        "page_name": "施工过程验收",
        "record_schema_count": 1,
        "sample_file": "sample_施工过程验收.json",
        "success_sample": true
    },
    {
        "api_name": "progInfo",
        "api_path": "/apit/ebuild2-domain-project-stage/v1/constrBoard/progInfo",
        "dataset_key": "dataset_dfc0835a",
        "has_record_schema": true,
        "page_name": "施工进度看板",
        "record_schema_count": 1,
        "sample_file": "sample_施工进度看板.json",
        "success_sample": true
    },
    {
        "api_name": "construction_progress_board_major_nodes",
        "api_path": "/apit/ebuild2-domain-project-stage/v1/constrBoard/progMajor",
        "dataset_key": "dataset_dfc0835a",
        "has_record_schema": true,
        "page_name": "施工进度看板",
        "record_schema_count": 2,
        "sample_file": "sample_施工进度看板.json",
        "success_sample": true
    },
    {
        "api_name": "queryBaseInfo",
        "api_path": "/apit/ebuild2-domain-project-stage/v1/constrPlan/queryBaseInfo",
        "dataset_key": "dataset_b419bad2",
        "has_record_schema": true,
        "page_name": "施工进度计划",
        "record_schema_count": 1,
        "sample_file": "sample_施工进度计划.json",
        "success_sample": true
    },
    {
        "api_name": "construction_schedule_major_nodes",
        "api_path": "/apit/ebuild2-domain-project-stage/v1/constrPlan/queryMajorInfo",
        "dataset_key": "dataset_b419bad2",
        "has_record_schema": true,
        "page_name": "施工进度计划",
        "record_schema_count": 2,
        "sample_file": "sample_施工进度计划.json",
        "success_sample": true
    },
    {
        "api_name": "adjust",
        "api_path": "/apit/ebuild2-domain-project-stage/v1/constrPlan/history/adjust",
        "dataset_key": "dataset_b419bad2",
        "has_record_schema": true,
        "page_name": "施工进度计划",
        "record_schema_count": 1,
        "sample_file": "sample_施工进度计划.json",
        "success_sample": true
    },
    {
        "api_name": "construction_dept_list",
        "api_path": "/apit/ebuild2-domain-project-form/v1/constructionDept/queryConstructionDeptListAPP",
        "dataset_key": "dataset_b0c41434",
        "has_record_schema": true,
        "page_name": "施工项目部",
        "record_schema_count": 1,
        "sample_file": "sample_施工项目部.json",
        "success_sample": true
    },
    {
        "api_name": "construction_dept_personnel",
        "api_path": "/apit/ebuild2-domain-project-form/v1/constructionPerson/queryDeptPerson",
        "dataset_key": "dataset_b0c41434",
        "has_record_schema": true,
        "page_name": "施工项目部",
        "record_schema_count": 2,
        "sample_file": "sample_施工项目部.json",
        "success_sample": true
    },
    {
        "api_name": "queryConstructionDeptFile",
        "api_path": "/apit/ebuild2-domain-project-form/v1/constructionDept/queryConstructionDeptFile",
        "dataset_key": "dataset_b0c41434",
        "has_record_schema": true,
        "page_name": "施工项目部",
        "record_schema_count": 1,
        "sample_file": "sample_施工项目部.json",
        "success_sample": true
    },
    {
        "api_name": "queryConstructionDeptProject",
        "api_path": "/apit/ebuild2-domain-project-form/v1/constructionProject/queryConstructionDeptProject",
        "dataset_key": "dataset_b0c41434",
        "has_record_schema": true,
        "page_name": "施工项目部",
        "record_schema_count": 3,
        "sample_file": "sample_施工项目部.json",
        "success_sample": true
    },
    {
        "api_name": "daily_plan",
        "api_path": "/apit/ebuild2-domain-security-work/v1/taskDaily/list",
        "dataset_key": "dataset_bba03ca4",
        "has_record_schema": false,
        "page_name": "日计划",
        "record_schema_count": 0,
        "sample_file": "sample_日计划.json",
        "success_sample": true
    },
    {
        "api_name": "countList",
        "api_path": "/apit/ebuild2-domain-security-work/v1/taskDaily/countList",
        "dataset_key": "dataset_bba03ca4",
        "has_record_schema": true,
        "page_name": "日计划",
        "record_schema_count": 1,
        "sample_file": "sample_日计划.json",
        "success_sample": true
    },
    {
        "api_name": "daily_plan_ledger",
        "api_path": "/apit/ebuild2-domain-security-work/v1/taskDaily/ledgerList",
        "dataset_key": "dataset_cc0f74c4",
        "has_record_schema": false,
        "page_name": "日计划一本账",
        "record_schema_count": 0,
        "sample_file": "sample_日计划一本账.json",
        "success_sample": true
    },
    {
        "api_name": "monthly_blackout_plan",
        "api_path": "/apit/ebuild2-domain-plan-foundation/v1/monthBlackoutPlan/queryMonthBlackoutPage",
        "dataset_key": "dataset_371fcd3d",
        "has_record_schema": true,
        "page_name": "月度停电计划上报与查看",
        "record_schema_count": 1,
        "sample_file": "sample_月度停电计划上报与查看.json",
        "success_sample": true
    },
    {
        "api_name": "monthly_blackout_plan_details",
        "api_path": "/apit/ebuild2-domain-plan-foundation/v1/monthBlackoutPlan/queryMonthBlackoutDetails",
        "dataset_key": "dataset_371fcd3d",
        "has_record_schema": true,
        "page_name": "月度停电计划上报与查看",
        "record_schema_count": 1,
        "sample_file": "sample_月度停电计划上报与查看.json",
        "success_sample": true
    },
    {
        "api_name": "detail",
        "api_path": "/apit/ebuild2-domain-project-stage/v1/tenderingService/detail",
        "dataset_key": "dataset_9002ea9c",
        "has_record_schema": true,
        "page_name": "服务类招标情况统计",
        "record_schema_count": 1,
        "sample_file": "sample_服务类招标情况统计.json",
        "success_sample": true
    },
    {
        "api_name": "construction_tender_contract",
        "api_path": "/apit/ebuild2-domain-plan-foundation/v1/supervisorTenderingContract/getPageResult",
        "dataset_key": "dataset_9002ea9c",
        "has_record_schema": true,
        "page_name": "服务类招标情况统计",
        "record_schema_count": 1,
        "sample_file": "sample_服务类招标情况统计.json",
        "success_sample": true
    },
    {
        "api_name": "getProjectListByContractId",
        "api_path": "/apit/ebuild2-domain-plan-foundation/v1/supervisorTenderingContract/getProjectListByContractId",
        "dataset_key": "dataset_9002ea9c",
        "has_record_schema": true,
        "page_name": "服务类招标情况统计",
        "record_schema_count": 1,
        "sample_file": "sample_服务类招标情况统计.json",
        "success_sample": true
    },
    {
        "api_name": "tower_single_projects",
        "api_path": "/apit/ebuild2-common-project-digitization/tower/getSingleProject",
        "dataset_key": "dataset_f58e1b9b",
        "has_record_schema": true,
        "page_name": "杆塔信息",
        "record_schema_count": 1,
        "sample_file": "sample_杆塔信息.json",
        "success_sample": true
    },
    {
        "api_name": "getBidSectBySinCode",
        "api_path": "/apit/ebuild2-common-project-digitization/tower/getBidSectBySinCode",
        "dataset_key": "dataset_f58e1b9b",
        "has_record_schema": true,
        "page_name": "杆塔信息",
        "record_schema_count": 1,
        "sample_file": "sample_杆塔信息.json",
        "success_sample": true
    },
    {
        "api_name": "tower_details",
        "api_path": "/apit/ebuild2-agg-cmm-service-center/tower/getTowerPageResult",
        "dataset_key": "dataset_f58e1b9b",
        "has_record_schema": true,
        "page_name": "杆塔信息",
        "record_schema_count": 1,
        "sample_file": "sample_杆塔信息.json",
        "success_sample": true
    },
    {
        "api_name": "queryToolBoxTalkStatus",
        "api_path": "/apit/ebuild2-domain-security-work/v1/toolBoxTalk/queryToolBoxTalkStatus",
        "dataset_key": "dataset_135eb70d",
        "has_record_schema": true,
        "page_name": "每日站班会",
        "record_schema_count": 1,
        "sample_file": "sample_每日站班会.json",
        "success_sample": true
    },
    {
        "api_name": "queryToolBoxTalkListPagePc",
        "api_path": "/apit/ebuild2-domain-security-work/v1/toolBoxTalk/queryToolBoxTalkListPagePc",
        "dataset_key": "dataset_135eb70d",
        "has_record_schema": false,
        "page_name": "每日站班会",
        "record_schema_count": 0,
        "sample_file": "sample_每日站班会.json",
        "success_sample": true
    },
    {
        "api_name": "getStatisticsPageResult",
        "api_path": "/apit/ebuild2-domain-plan-foundation/v1/materialTenderingInfo/getStatisticsPageResult",
        "dataset_key": "dataset_64d9153f",
        "has_record_schema": true,
        "page_name": "物资类招标情况统计",
        "record_schema_count": 1,
        "sample_file": "sample_物资类招标情况统计.json",
        "success_sample": true
    },
    {
        "api_name": "getMaterialTenderingInfoPageResult",
        "api_path": "/apit/ebuild2-domain-plan-foundation/v1/materialTenderingInfo/getMaterialTenderingInfoPageResult",
        "dataset_key": "dataset_64d9153f",
        "has_record_schema": true,
        "page_name": "物资类招标情况统计",
        "record_schema_count": 1,
        "sample_file": "sample_物资类招标情况统计.json",
        "success_sample": true
    },
    {
        "api_name": "site_instruction_approval",
        "api_path": "/apit/ebuild2-domain-economy-manage/v1/instruction/queryInstructionApprovalPage",
        "dataset_key": "dataset_36f2621e",
        "has_record_schema": true,
        "page_name": "现场签证审批单",
        "record_schema_count": 1,
        "sample_file": "sample_现场签证审批单.json",
        "success_sample": true
    },
    {
        "api_name": "queryInstructionApprovalCount",
        "api_path": "/apit/ebuild2-domain-economy-manage/v1/instruction/queryInstructionApprovalCount",
        "dataset_key": "dataset_36f2621e",
        "has_record_schema": true,
        "page_name": "现场签证审批单",
        "record_schema_count": 1,
        "sample_file": "sample_现场签证审批单.json",
        "success_sample": true
    },
    {
        "api_name": "working_team_dissolved",
        "api_path": "/apit/ebuild2-domain-security-work/v1/team/queryWorkingTeamPage",
        "dataset_key": "dataset_5e6c0f3e",
        "has_record_schema": true,
        "page_name": "班组组建",
        "record_schema_count": 5,
        "sample_file": "sample_班组组建.json",
        "success_sample": true
    },
    {
        "api_name": "construction_tender_contract",
        "api_path": "/apit/ebuild2-domain-plan-foundation/v1/supervisorTenderingContract/getPageResult",
        "dataset_key": "dataset_627918af",
        "has_record_schema": true,
        "page_name": "监理招投标及合同",
        "record_schema_count": 1,
        "sample_file": "sample_监理招投标及合同.json",
        "success_sample": true
    },
    {
        "api_name": "supervision_outline",
        "api_path": "/apit/ebuild2-domain-project-stage/v1/supervisorScheme/querySupervisorSchemePage",
        "dataset_key": "dataset_bdbab29b",
        "has_record_schema": true,
        "page_name": "监理策划",
        "record_schema_count": 3,
        "sample_file": "sample_监理策划.json",
        "success_sample": true
    },
    {
        "api_name": "supervision_dept_list",
        "api_path": "/apit/ebuild2-domain-project-form/v1/supervisorDept/queryDeptListAPP",
        "dataset_key": "dataset_0e8c85a2",
        "has_record_schema": true,
        "page_name": "监理项目部",
        "record_schema_count": 1,
        "sample_file": "sample_监理项目部.json",
        "success_sample": true
    },
    {
        "api_name": "supervision_dept_personnel",
        "api_path": "/apit/ebuild2-domain-project-form/v1/supervisorPerson/querySupervisorDeptPerson",
        "dataset_key": "dataset_0e8c85a2",
        "has_record_schema": true,
        "page_name": "监理项目部",
        "record_schema_count": 2,
        "sample_file": "sample_监理项目部.json",
        "success_sample": true
    },
    {
        "api_name": "queryDeptFile",
        "api_path": "/apit/ebuild2-domain-project-form/v1/supervisorDept/queryDeptFile",
        "dataset_key": "dataset_0e8c85a2",
        "has_record_schema": true,
        "page_name": "监理项目部",
        "record_schema_count": 1,
        "sample_file": "sample_监理项目部.json",
        "success_sample": true
    },
    {
        "api_name": "querySupervisorDeptProject",
        "api_path": "/apit/ebuild2-domain-project-form/v1/supervisorProject/querySupervisorDeptProject",
        "dataset_key": "dataset_0e8c85a2",
        "has_record_schema": true,
        "page_name": "监理项目部",
        "record_schema_count": 3,
        "sample_file": "sample_监理项目部.json",
        "success_sample": true
    },
    {
        "api_name": "completion_acceptance_list",
        "api_path": "/apit/ebuild2-domain-project-stage/v1/completionAcceptance/getInfo",
        "dataset_key": "dataset_3a1b7207",
        "has_record_schema": true,
        "page_name": "竣工预验收",
        "record_schema_count": 7,
        "sample_file": "sample_竣工预验收.json",
        "success_sample": true
    },
    {
        "api_name": "completion_acceptance_details",
        "api_path": "/apit/ebuild2-domain-project-stage/v1/completionAcceptance/geQrySinAndBidInfo",
        "dataset_key": "dataset_3a1b7207",
        "has_record_schema": true,
        "page_name": "竣工预验收",
        "record_schema_count": 4,
        "sample_file": "sample_竣工预验收.json",
        "success_sample": true
    },
    {
        "api_name": "plan_completion_reports",
        "api_path": "/apit/ebuild2-domain-plan-statistics/v1/projectInventory/queryProjectInventoryList",
        "dataset_key": "dataset_b7dcfdb4",
        "has_record_schema": true,
        "page_name": "计划完成情况统计",
        "record_schema_count": 1,
        "sample_file": "sample_计划完成情况统计.json",
        "success_sample": true
    },
    {
        "api_name": "queryQualityCheckList",
        "api_path": "/apit/ebuild2-domain-quality-manage/v1/work/queryQualityCheckList",
        "dataset_key": "dataset_ba43ddfc",
        "has_record_schema": false,
        "page_name": "设备材料缺陷",
        "record_schema_count": 0,
        "sample_file": "sample_设备材料缺陷.json",
        "success_sample": true
    },
    {
        "api_name": "page",
        "api_path": "/apit/ebuild2-domain-quality-manage/v1/device/page",
        "dataset_key": "dataset_dbc8499e",
        "has_record_schema": false,
        "page_name": "设备缺陷处理",
        "record_schema_count": 0,
        "sample_file": "sample_设备缺陷处理.json",
        "success_sample": true
    },
    {
        "api_name": "design_change_approval",
        "api_path": "/apit/ebuild2-domain-economy-manage/v1/changeApproval/changeApprovalPage",
        "dataset_key": "dataset_8a28eaaf",
        "has_record_schema": true,
        "page_name": "设计变更审批单",
        "record_schema_count": 1,
        "sample_file": "sample_设计变更审批单.json",
        "success_sample": true
    },
    {
        "api_name": "countDesignDealData",
        "api_path": "/apit/ebuild2-domain-economy-manage/v1/changeApproval/countDesignDealData",
        "dataset_key": "dataset_8a28eaaf",
        "has_record_schema": true,
        "page_name": "设计变更审批单",
        "record_schema_count": 1,
        "sample_file": "sample_设计变更审批单.json",
        "success_sample": true
    },
    {
        "api_name": "design_dept_list",
        "api_path": "/apit/ebuild2-domain-project-form/v1/designDept/queryDeptListAPP",
        "dataset_key": "dataset_2981b5b1",
        "has_record_schema": true,
        "page_name": "设计项目部",
        "record_schema_count": 1,
        "sample_file": "sample_设计项目部.json",
        "success_sample": true
    },
    {
        "api_name": "design_dept_personnel",
        "api_path": "/apit/ebuild2-domain-project-form/v1/designPerson/queryDesignDeptPerson",
        "dataset_key": "dataset_2981b5b1",
        "has_record_schema": true,
        "page_name": "设计项目部",
        "record_schema_count": 2,
        "sample_file": "sample_设计项目部.json",
        "success_sample": true
    },
    {
        "api_name": "queryDesignDeptFile",
        "api_path": "/apit/ebuild2-domain-project-form/v1/designDept/queryDesignDeptFile",
        "dataset_key": "dataset_2981b5b1",
        "has_record_schema": true,
        "page_name": "设计项目部",
        "record_schema_count": 1,
        "sample_file": "sample_设计项目部.json",
        "success_sample": true
    },
    {
        "api_name": "queryDesignDeptProject",
        "api_path": "/apit/ebuild2-domain-project-form/v1/designProject/queryDesignDeptProject",
        "dataset_key": "dataset_2981b5b1",
        "has_record_schema": true,
        "page_name": "设计项目部",
        "record_schema_count": 2,
        "sample_file": "sample_设计项目部.json",
        "success_sample": true
    },
    {
        "api_name": "queryMainDeviceApproval",
        "api_path": "/apit/ebuild2-domain-quality-accept/v1/mainDevice/queryMainDeviceApproval",
        "dataset_key": "dataset_fa299629",
        "has_record_schema": false,
        "page_name": "试验调试报告审查",
        "record_schema_count": 0,
        "sample_file": "sample_试验调试报告审查.json",
        "success_sample": true
    },
    {
        "api_name": "queryMainDeviceApproval",
        "api_path": "/apit/ebuild2-domain-quality-accept/v1/mainDevice/queryMainDeviceApproval",
        "dataset_key": "dataset_0945e77c",
        "has_record_schema": false,
        "page_name": "试验调试报告查看",
        "record_schema_count": 0,
        "sample_file": "sample_试验调试报告查看.json",
        "success_sample": true
    },
    {
        "api_name": "queryWorkItemInitList",
        "api_path": "/apit/ebuild2-domain-quality-manage/v1/init/queryWorkItemInitList",
        "dataset_key": "dataset_726638d3",
        "has_record_schema": true,
        "page_name": "质量检测计划",
        "record_schema_count": 1,
        "sample_file": "sample_质量检测计划.json",
        "success_sample": true
    },
    {
        "api_name": "queryCheckSchduleApplyList",
        "api_path": "/apit/ebuild2-domain-quality-manage/v1/work/queryCheckSchduleApplyList",
        "dataset_key": "dataset_726638d3",
        "has_record_schema": false,
        "page_name": "质量检测计划",
        "record_schema_count": 0,
        "sample_file": "sample_质量检测计划.json",
        "success_sample": true
    },
    {
        "api_name": "getCheckCountTitle",
        "api_path": "/apit/ebuild2-domain-quality-accept/v1/checkCount/getCheckCountTitle",
        "dataset_key": "dataset_784b6267",
        "has_record_schema": true,
        "page_name": "质量验收汇总",
        "record_schema_count": 1,
        "sample_file": "sample_质量验收汇总.json",
        "success_sample": true
    },
    {
        "api_name": "getCheckCountList",
        "api_path": "/apit/ebuild2-domain-quality-accept/v1/checkCount/getCheckCountList",
        "dataset_key": "dataset_784b6267",
        "has_record_schema": true,
        "page_name": "质量验收汇总",
        "record_schema_count": 1,
        "sample_file": "sample_质量验收汇总.json",
        "success_sample": true
    },
    {
        "api_name": "queryProjectInfoListPage",
        "api_path": "/apit/ebuild2-domain-project-form/v1/projectInformation/queryProjectInfoListPage",
        "dataset_key": "dataset_eac2e191",
        "has_record_schema": true,
        "page_name": "项目信息查询",
        "record_schema_count": 1,
        "sample_file": "sample_项目信息查询.json",
        "success_sample": true
    },
    {
        "api_name": "project_reserve_pool",
        "api_path": "/apit/ebuild2-domain-project-form/v1/preparation/getReserveInfo",
        "dataset_key": "dataset_26f597c7",
        "has_record_schema": true,
        "page_name": "项目储备库查看",
        "record_schema_count": 1,
        "sample_file": "sample_项目储备库查看.json",
        "success_sample": true
    },
    {
        "api_name": "preconstruction_results_detail",
        "api_path": "/apit/ebuild2-domain-project-form/v1/projectInfoGet/one/queryDetail",
        "dataset_key": "dataset_6ae53ddc",
        "has_record_schema": true,
        "page_name": "项目前期成果",
        "record_schema_count": 6,
        "sample_file": "sample_项目前期成果.json",
        "success_sample": true
    },
    {
        "api_name": "preconstruction_results_detail",
        "api_path": "/apit/ebuild2-domain-project-form/v1/projectInfoGet/queryDetail",
        "dataset_key": "dataset_de3264f2",
        "has_record_schema": true,
        "page_name": "项目基本信息",
        "record_schema_count": 6,
        "sample_file": "sample_项目基本信息.json",
        "success_sample": true
    },
    {
        "api_name": "implementation_plan",
        "api_path": "/apit/ebuild2-domain-project-stage/v1/implPlan/queryImplNodes",
        "dataset_key": "dataset_f313e3e9",
        "has_record_schema": true,
        "page_name": "项目实施计划",
        "record_schema_count": 1,
        "sample_file": "sample_项目实施计划.json",
        "success_sample": true
    },
    {
        "api_name": "project_management",
        "api_path": "/apit/ebuild2-domain-project-form/v1/projectInfoGet/queryList",
        "dataset_key": "dataset_4f9a248d",
        "has_record_schema": true,
        "page_name": "项目管理",
        "record_schema_count": 3,
        "sample_file": "sample_项目管理.json",
        "success_sample": true
    },
    {
        "api_name": "construction_outline",
        "api_path": "/apit/ebuild2-domain-project-stage/v1/implementPlanning/queryImplementPlanningPage",
        "dataset_key": "dataset_98117e03",
        "has_record_schema": true,
        "page_name": "项目管理实施规划",
        "record_schema_count": 3,
        "sample_file": "sample_项目管理实施规划.json",
        "success_sample": true
    },
    {
        "api_name": "project_department_key_personnel",
        "api_path": "/apit/ebuild2-domain-plan-statistics/v1/dept/queryKeyPersonnelInfo",
        "dataset_key": "dataset_7563ad12",
        "has_record_schema": true,
        "page_name": "项目部关键人员统计",
        "record_schema_count": 2,
        "sample_file": "sample_项目部关键人员统计.json",
        "success_sample": true
    },
    {
        "api_name": "project_department_establishment",
        "api_path": "/apit/ebuild2-domain-plan-statistics/v1/dept/queryProjectDeptDetail",
        "dataset_key": "dataset_93667e3b",
        "has_record_schema": true,
        "page_name": "项目部组建情况统计",
        "record_schema_count": 1,
        "sample_file": "sample_项目部组建情况统计.json",
        "success_sample": true
    },
    {
        "api_name": "project_evaluation",
        "api_path": "/apit/ebuild2-domain-project-stage/v1/summaryEvaluate/queryDeptSummaryList",
        "dataset_key": "dataset_ecce9198",
        "has_record_schema": true,
        "page_name": "项目部评价汇总",
        "record_schema_count": 2,
        "sample_file": "sample_项目部评价汇总.json",
        "success_sample": true
    },
    {
        "api_name": "risk_ledger_list",
        "api_path": "/apit/ebuild2-domain-security-risk/v1/projectRiskLedger/queryPage",
        "dataset_key": "dataset_0a75165a",
        "has_record_schema": true,
        "page_name": "风险底数一本账",
        "record_schema_count": 2,
        "sample_file": "sample_风险底数一本账.json",
        "success_sample": true
    },
    {
        "api_name": "page",
        "api_path": "/apit/ebuild2-domain-quality-accept/v1/divide/page",
        "dataset_key": "dataset_74015418",
        "has_record_schema": true,
        "page_name": "验收范围划分",
        "record_schema_count": 1,
        "sample_file": "sample_验收范围划分.json",
        "success_sample": true
    }
]

DCP_RESPONSE_TABLES = [
    {
        "api_name": "owner_dept_list",
        "api_path": "/apit/ebuild2-domain-project-form/v1/ownerDept/queryDeptListAPP",
        "columns": [
            {
                "name": "address",
                "source": "address",
                "type": "TEXT"
            },
            {
                "name": "affiliationCode",
                "source": "affiliationCode",
                "type": "TEXT"
            },
            {
                "name": "affiliationName",
                "source": "affiliationName",
                "type": "TEXT"
            },
            {
                "name": "bpmId",
                "source": "bpmId",
                "type": "TEXT"
            },
            {
                "name": "buildUnitCode",
                "source": "buildUnitCode",
                "type": "TEXT"
            },
            {
                "name": "contactTelephone",
                "source": "contactTelephone",
                "type": "TEXT"
            },
            {
                "name": "createTime",
                "source": "createTime",
                "type": "INTEGER"
            },
            {
                "name": "createrId",
                "source": "createrId",
                "type": "TEXT"
            },
            {
                "name": "deleteFlag",
                "source": "deleteFlag",
                "type": "INTEGER"
            },
            {
                "name": "departmentStatus",
                "source": "departmentStatus",
                "type": "INTEGER"
            },
            {
                "name": "departmentType",
                "source": "departmentType",
                "type": "INTEGER"
            },
            {
                "name": "deptCitiesCode",
                "source": "deptCitiesCode",
                "type": "INTEGER"
            },
            {
                "name": "deptCitiesName",
                "source": "deptCitiesName",
                "type": "TEXT"
            },
            {
                "name": "deptDistrictCode",
                "source": "deptDistrictCode",
                "type": "INTEGER"
            },
            {
                "name": "deptDistrictName",
                "source": "deptDistrictName",
                "type": "TEXT"
            },
            {
                "name": "deptId",
                "source": "deptId",
                "type": "TEXT"
            },
            {
                "name": "deptProvinceCode",
                "source": "deptProvinceCode",
                "type": "TEXT"
            },
            {
                "name": "deptProvinceName",
                "source": "deptProvinceName",
                "type": "TEXT"
            },
            {
                "name": "emailAddress",
                "source": "emailAddress",
                "type": "TEXT"
            },
            {
                "name": "establishingMode",
                "source": "establishingMode",
                "type": "INTEGER"
            },
            {
                "name": "establishmentDate",
                "source": "establishmentDate",
                "type": "TEXT"
            },
            {
                "name": "extra",
                "source": "extra",
                "type": "TEXT"
            },
            {
                "name": "faxNo",
                "source": "faxNo",
                "type": "TEXT"
            },
            {
                "name": "groupMarkup",
                "source": "groupMarkup",
                "type": "INTEGER"
            },
            {
                "name": "historyFlag",
                "source": "historyFlag",
                "type": "INTEGER"
            },
            {
                "name": "isHaveReset",
                "source": "isHaveReset",
                "type": "TEXT"
            },
            {
                "name": "postalCode",
                "source": "postalCode",
                "type": "TEXT"
            },
            {
                "name": "projectDepartmentName",
                "source": "projectDepartmentName",
                "type": "TEXT"
            },
            {
                "name": "projectDeptNo",
                "source": "projectDeptNo",
                "type": "TEXT"
            },
            {
                "name": "provinceCode",
                "source": "provinceCode",
                "type": "TEXT"
            },
            {
                "name": "realName",
                "source": "realName",
                "type": "TEXT"
            },
            {
                "name": "singnFlag",
                "source": "singnFlag",
                "type": "TEXT"
            },
            {
                "name": "traceId",
                "source": "traceId",
                "type": "TEXT"
            },
            {
                "name": "updateTime",
                "source": "updateTime",
                "type": "INTEGER"
            },
            {
                "name": "updaterId",
                "source": "updaterId",
                "type": "TEXT"
            },
            {
                "name": "year",
                "source": "year",
                "type": "TEXT"
            }
        ],
        "dataset_key": "dataset_d32cb9ff",
        "key_candidates": [
            "source_record_key+record_path"
        ],
        "page_name": "业主项目部",
        "parent_record_path": null,
        "partition_field": null,
        "partition_key": null,
        "plugin_id": "dcp-dataset-d32cb9ff",
        "record_path": "raw_event",
        "record_type": "owner_dept_list:raw_event",
        "table": "canonical_p001_page_d32cb9ff__owner_dept_list__raw_event"
    },
    {
        "api_name": "owner_dept_personnel",
        "api_path": "/apit/ebuild2-domain-project-form/v1/ownerPerson/queryDeptPerson",
        "columns": [
            {
                "name": "beforeId",
                "source": "beforeId",
                "type": "TEXT"
            },
            {
                "name": "beforeName",
                "source": "beforeName",
                "type": "TEXT"
            },
            {
                "name": "buildername",
                "source": "buildername",
                "type": "TEXT"
            },
            {
                "name": "certificates",
                "source": "certificates",
                "type": "TEXT"
            },
            {
                "name": "changeFlag",
                "source": "changeFlag",
                "type": "TEXT"
            },
            {
                "name": "constrCertificate",
                "source": "constrCertificate",
                "type": "TEXT"
            },
            {
                "name": "deleteFlag",
                "source": "deleteFlag",
                "type": "TEXT"
            },
            {
                "name": "deptKey",
                "source": "deptKey",
                "type": "INTEGER"
            },
            {
                "name": "dprId",
                "source": "dprId",
                "type": "TEXT"
            },
            {
                "name": "engineerRecordId",
                "source": "engineerRecordId",
                "type": "TEXT"
            },
            {
                "name": "entryDate",
                "source": "entryDate",
                "type": "TEXT"
            },
            {
                "name": "exitDate",
                "source": "exitDate",
                "type": "TEXT"
            },
            {
                "name": "extra",
                "source": "extra",
                "type": "TEXT"
            },
            {
                "name": "gender",
                "source": "gender",
                "type": "TEXT"
            },
            {
                "name": "historyFlag",
                "source": "historyFlag",
                "type": "TEXT"
            },
            {
                "name": "id",
                "source": "id",
                "type": "TEXT"
            },
            {
                "name": "idCard",
                "source": "idCard",
                "type": "TEXT"
            },
            {
                "name": "idCardTO",
                "source": "idCardTO",
                "type": "TEXT"
            },
            {
                "name": "jobCode",
                "source": "jobCode",
                "type": "TEXT"
            },
            {
                "name": "jobName",
                "source": "jobName",
                "type": "TEXT"
            },
            {
                "name": "mobile",
                "source": "mobile",
                "type": "TEXT"
            },
            {
                "name": "mobileTO",
                "source": "mobileTO",
                "type": "TEXT"
            },
            {
                "name": "personnelCap",
                "source": "personnelCap",
                "type": "INTEGER"
            },
            {
                "name": "positionCode",
                "source": "positionCode",
                "type": "TEXT"
            },
            {
                "name": "positionName",
                "source": "positionName",
                "type": "TEXT"
            },
            {
                "name": "projectDepartmentId",
                "source": "projectDepartmentId",
                "type": "TEXT"
            },
            {
                "name": "provinceCode",
                "source": "provinceCode",
                "type": "TEXT"
            },
            {
                "name": "provinceCodeText",
                "source": "provinceCodeText",
                "type": "TEXT"
            },
            {
                "name": "realName",
                "source": "realName",
                "type": "TEXT"
            },
            {
                "name": "realNameTO",
                "source": "realNameTO",
                "type": "TEXT"
            },
            {
                "name": "specialty",
                "source": "specialty",
                "type": "TEXT"
            },
            {
                "name": "statusState",
                "source": "statusState",
                "type": "TEXT"
            },
            {
                "name": "traceId",
                "source": "traceId",
                "type": "TEXT"
            },
            {
                "name": "unitName",
                "source": "unitName",
                "type": "TEXT"
            },
            {
                "name": "withinFlag",
                "source": "withinFlag",
                "type": "TEXT"
            }
        ],
        "dataset_key": "dataset_d32cb9ff",
        "key_candidates": [
            "id"
        ],
        "page_name": "业主项目部",
        "parent_record_path": null,
        "partition_field": null,
        "partition_key": null,
        "plugin_id": "dcp-dataset-d32cb9ff",
        "record_path": "raw_event",
        "record_type": "owner_dept_personnel:raw_event",
        "table": "canonical_p001_page_d32cb9ff__owner_dept_personnel__raw_event"
    },
    {
        "api_name": "queryDeptFile",
        "api_path": "/apit/ebuild2-domain-project-form/v1/ownerDept/queryDeptFile",
        "columns": [
            {
                "name": "approvalNode",
                "source": "approvalNode",
                "type": "INTEGER"
            },
            {
                "name": "authorizationMatter",
                "source": "authorizationMatter",
                "type": "TEXT"
            },
            {
                "name": "certificateName",
                "source": "certificateName",
                "type": "TEXT"
            },
            {
                "name": "certificateNo",
                "source": "certificateNo",
                "type": "TEXT"
            },
            {
                "name": "deleteFlag",
                "source": "deleteFlag",
                "type": "INTEGER"
            },
            {
                "name": "documentClass",
                "source": "documentClass",
                "type": "INTEGER"
            },
            {
                "name": "extra",
                "source": "extra",
                "type": "TEXT"
            },
            {
                "name": "fileId",
                "source": "fileId",
                "type": "TEXT"
            },
            {
                "name": "fileName",
                "source": "fileName",
                "type": "TEXT"
            },
            {
                "name": "id",
                "source": "id",
                "type": "TEXT"
            },
            {
                "name": "instanceId",
                "source": "instanceId",
                "type": "TEXT"
            },
            {
                "name": "isHaveReset",
                "source": "isHaveReset",
                "type": "TEXT"
            },
            {
                "name": "personnelId",
                "source": "personnelId",
                "type": "TEXT"
            },
            {
                "name": "practiceQualification",
                "source": "practiceQualification",
                "type": "TEXT"
            },
            {
                "name": "prjCode",
                "source": "prjCode",
                "type": "TEXT"
            },
            {
                "name": "prjName",
                "source": "prjName",
                "type": "TEXT"
            },
            {
                "name": "projectDepartmentId",
                "source": "projectDepartmentId",
                "type": "TEXT"
            },
            {
                "name": "signTime",
                "source": "signTime",
                "type": "TEXT"
            },
            {
                "name": "signatureFlag",
                "source": "signatureFlag",
                "type": "INTEGER"
            },
            {
                "name": "signaturesStatus",
                "source": "signaturesStatus",
                "type": "INTEGER"
            },
            {
                "name": "singnFlag",
                "source": "singnFlag",
                "type": "INTEGER"
            },
            {
                "name": "traceId",
                "source": "traceId",
                "type": "TEXT"
            }
        ],
        "dataset_key": "dataset_d32cb9ff",
        "key_candidates": [
            "id",
            "prjCode"
        ],
        "page_name": "业主项目部",
        "parent_record_path": null,
        "partition_field": "prjCode",
        "partition_key": "prjCode",
        "plugin_id": "dcp-dataset-d32cb9ff",
        "record_path": "raw_event",
        "record_type": "queryDeptFile:raw_event",
        "table": "canonical_p001_page_d32cb9ff__querydeptfile__raw_event"
    },
    {
        "api_name": "queryOwnerDeptProject",
        "api_path": "/apit/ebuild2-domain-project-form/v1/ownerProject/queryOwnerDeptProject",
        "columns": [
            {
                "name": "actualCommencementDate",
                "source": "actualCommencementDate",
                "type": "TEXT"
            },
            {
                "name": "actualCommissioningDate",
                "source": "actualCommissioningDate",
                "type": "TEXT"
            },
            {
                "name": "constrNature",
                "source": "constrNature",
                "type": "TEXT"
            },
            {
                "name": "constrNatureText",
                "source": "constrNatureText",
                "type": "TEXT"
            },
            {
                "name": "constrTransformerCapacity",
                "source": "constrTransformerCapacity",
                "type": "REAL"
            },
            {
                "name": "constructionLineLength",
                "source": "constructionLineLength",
                "type": "REAL"
            },
            {
                "name": "extra",
                "source": "extra",
                "type": "TEXT"
            },
            {
                "name": "isCancel",
                "source": "isCancel",
                "type": "INTEGER"
            },
            {
                "name": "isDeptManage",
                "source": "isDeptManage",
                "type": "TEXT"
            },
            {
                "name": "plannedCommencementDate",
                "source": "plannedCommencementDate",
                "type": "TEXT"
            },
            {
                "name": "plannedCommissioningDate",
                "source": "plannedCommissioningDate",
                "type": "TEXT"
            },
            {
                "name": "prjCode",
                "source": "prjCode",
                "type": "TEXT"
            },
            {
                "name": "prjManageMode",
                "source": "prjManageMode",
                "type": "TEXT"
            },
            {
                "name": "prjName",
                "source": "prjName",
                "type": "TEXT"
            },
            {
                "name": "projectManagement",
                "source": "projectManagement",
                "type": "TEXT"
            },
            {
                "name": "sortNum",
                "source": "sortNum",
                "type": "TEXT"
            },
            {
                "name": "traceId",
                "source": "traceId",
                "type": "TEXT"
            },
            {
                "name": "voltageLevel",
                "source": "voltageLevel",
                "type": "TEXT"
            },
            {
                "name": "voltageLevelText",
                "source": "voltageLevelText",
                "type": "TEXT"
            }
        ],
        "dataset_key": "dataset_d32cb9ff",
        "key_candidates": [
            "prjCode"
        ],
        "page_name": "业主项目部",
        "parent_record_path": null,
        "partition_field": "prjCode",
        "partition_key": "prjCode",
        "plugin_id": "dcp-dataset-d32cb9ff",
        "record_path": "raw_event",
        "record_type": "queryOwnerDeptProject:raw_event",
        "table": "canonical_p001_page_d32cb9ff__queryownerdeptproject__raw_event"
    },
    {
        "api_name": "queryOwnerDeptProject",
        "api_path": "/apit/ebuild2-domain-project-form/v1/ownerProject/queryOwnerDeptProject",
        "columns": [
            {
                "name": "actualCommencementDate",
                "source": "actualCommencementDate",
                "type": "TEXT"
            },
            {
                "name": "actualCommissioningDate",
                "source": "actualCommissioningDate",
                "type": "TEXT"
            },
            {
                "name": "bidSectDTOS",
                "source": "bidSectDTOS",
                "type": "TEXT"
            },
            {
                "name": "buildUnitCode",
                "source": "buildUnitCode",
                "type": "TEXT"
            },
            {
                "name": "buildUnitName",
                "source": "buildUnitName",
                "type": "TEXT"
            },
            {
                "name": "constrNature",
                "source": "constrNature",
                "type": "INTEGER"
            },
            {
                "name": "constrNatureText",
                "source": "constrNatureText",
                "type": "TEXT"
            },
            {
                "name": "constrTransformerCapacity",
                "source": "constrTransformerCapacity",
                "type": "REAL"
            },
            {
                "name": "constructionLineLength",
                "source": "constructionLineLength",
                "type": "TEXT"
            },
            {
                "name": "contractId",
                "source": "contractId",
                "type": "TEXT"
            },
            {
                "name": "extra",
                "source": "extra",
                "type": "TEXT"
            },
            {
                "name": "isCancel",
                "source": "isCancel",
                "type": "INTEGER"
            },
            {
                "name": "personnelDTOS",
                "source": "personnelDTOS",
                "type": "TEXT"
            },
            {
                "name": "plannedCommencementDate",
                "source": "plannedCommencementDate",
                "type": "TEXT"
            },
            {
                "name": "plannedCommissioningDate",
                "source": "plannedCommissioningDate",
                "type": "TEXT"
            },
            {
                "name": "prjCode",
                "source": "prjCode",
                "type": "TEXT"
            },
            {
                "name": "prjName",
                "source": "prjName",
                "type": "TEXT"
            },
            {
                "name": "projectManagement",
                "source": "projectManagement",
                "type": "TEXT"
            },
            {
                "name": "provinceCode",
                "source": "provinceCode",
                "type": "TEXT"
            },
            {
                "name": "provinceName",
                "source": "provinceName",
                "type": "TEXT"
            },
            {
                "name": "singleProjectCode",
                "source": "singleProjectCode",
                "type": "TEXT"
            },
            {
                "name": "singleProjectName",
                "source": "singleProjectName",
                "type": "TEXT"
            },
            {
                "name": "sortNum",
                "source": "sortNum",
                "type": "TEXT"
            },
            {
                "name": "traceId",
                "source": "traceId",
                "type": "TEXT"
            },
            {
                "name": "voltageLevel",
                "source": "voltageLevel",
                "type": "TEXT"
            }
        ],
        "dataset_key": "dataset_d32cb9ff",
        "key_candidates": [
            "prjCode",
            "singleProjectCode",
            "prjCode+singleProjectCode"
        ],
        "page_name": "业主项目部",
        "parent_record_path": "raw_event",
        "partition_field": "prjCode",
        "partition_key": "prjCode",
        "plugin_id": "dcp-dataset-d32cb9ff",
        "record_path": "raw_event.sinPrjDTOS[]",
        "record_type": "queryOwnerDeptProject:raw_event.sinPrjDTOS[]",
        "table": "canonical_p001_page_d32cb9ff__queryownerdeptproject__raw_event_sinprjdtos_items"
    },
    {
        "api_name": "queryAllEquipTypeName",
        "api_path": "/apit/ebuild2-domain-quality-accept/v1/mainDevice/queryAllEquipTypeName",
        "columns": [
            {
                "name": "count",
                "source": "count",
                "type": "TEXT"
            },
            {
                "name": "disable",
                "source": "disable",
                "type": "TEXT"
            },
            {
                "name": "equipTypeCode",
                "source": "equipTypeCode",
                "type": "TEXT"
            },
            {
                "name": "equipTypeName",
                "source": "equipTypeName",
                "type": "TEXT"
            }
        ],
        "dataset_key": "dataset_acc32ade",
        "key_candidates": [
            "source_record_key+record_path"
        ],
        "page_name": "主设备清单维护",
        "parent_record_path": null,
        "partition_field": null,
        "partition_key": null,
        "plugin_id": "dcp-dataset-acc32ade",
        "record_path": "raw_event",
        "record_type": "queryAllEquipTypeName:raw_event",
        "table": "canonical_p002_page_acc32ade__queryallequiptypename__raw_event"
    },
    {
        "api_name": "worksite_substation",
        "api_path": "/apit/ebuild2-domain-security-risk/v1/worksite/querySubstationPage",
        "columns": [
            {
                "name": "address",
                "source": "address",
                "type": "TEXT"
            },
            {
                "name": "biddingSectionCode",
                "source": "biddingSectionCode",
                "type": "TEXT"
            },
            {
                "name": "biddingSectionName",
                "source": "biddingSectionName",
                "type": "TEXT"
            },
            {
                "name": "children",
                "source": "children",
                "type": "TEXT"
            },
            {
                "name": "extra",
                "source": "extra",
                "type": "TEXT"
            },
            {
                "name": "id",
                "source": "id",
                "type": "TEXT"
            },
            {
                "name": "latitude",
                "source": "latitude",
                "type": "TEXT"
            },
            {
                "name": "longitude",
                "source": "longitude",
                "type": "TEXT"
            },
            {
                "name": "parentId",
                "source": "parentId",
                "type": "TEXT"
            },
            {
                "name": "parentName",
                "source": "parentName",
                "type": "TEXT"
            },
            {
                "name": "prjCode",
                "source": "prjCode",
                "type": "TEXT"
            },
            {
                "name": "prjName",
                "source": "prjName",
                "type": "TEXT"
            },
            {
                "name": "readOnly",
                "source": "readOnly",
                "type": "TEXT"
            },
            {
                "name": "singleProjectCode",
                "source": "singleProjectCode",
                "type": "TEXT"
            },
            {
                "name": "singleProjectName",
                "source": "singleProjectName",
                "type": "TEXT"
            },
            {
                "name": "traceId",
                "source": "traceId",
                "type": "TEXT"
            },
            {
                "name": "updateTime",
                "source": "updateTime",
                "type": "TEXT"
            },
            {
                "name": "updater",
                "source": "updater",
                "type": "TEXT"
            },
            {
                "name": "updaterId",
                "source": "updaterId",
                "type": "TEXT"
            },
            {
                "name": "workSiteName",
                "source": "workSiteName",
                "type": "TEXT"
            }
        ],
        "dataset_key": "dataset_5f5a4fcf",
        "key_candidates": [
            "id",
            "prjCode",
            "singleProjectCode",
            "biddingSectionCode",
            "prjCode+singleProjectCode+biddingSectionCode"
        ],
        "page_name": "作业部位管理",
        "parent_record_path": null,
        "partition_field": "prjCode",
        "partition_key": "prjCode",
        "plugin_id": "dcp-dataset-5f5a4fcf",
        "record_path": "raw_event",
        "record_type": "worksite_substation:raw_event",
        "table": "canonical_p003_page_5f5a4fcf__worksite_substation__raw_event"
    },
    {
        "api_name": "worksite_substation",
        "api_path": "/apit/ebuild2-domain-security-risk/v1/worksite/querySubstationPage",
        "columns": [
            {
                "name": "address",
                "source": "address",
                "type": "TEXT"
            },
            {
                "name": "biddingSectionCode",
                "source": "biddingSectionCode",
                "type": "TEXT"
            },
            {
                "name": "biddingSectionName",
                "source": "biddingSectionName",
                "type": "TEXT"
            },
            {
                "name": "children",
                "source": "children",
                "type": "TEXT"
            },
            {
                "name": "extra",
                "source": "extra",
                "type": "TEXT"
            },
            {
                "name": "id",
                "source": "id",
                "type": "TEXT"
            },
            {
                "name": "latitude",
                "source": "latitude",
                "type": "TEXT"
            },
            {
                "name": "longitude",
                "source": "longitude",
                "type": "TEXT"
            },
            {
                "name": "parentId",
                "source": "parentId",
                "type": "TEXT"
            },
            {
                "name": "parentName",
                "source": "parentName",
                "type": "TEXT"
            },
            {
                "name": "prjCode",
                "source": "prjCode",
                "type": "TEXT"
            },
            {
                "name": "prjName",
                "source": "prjName",
                "type": "TEXT"
            },
            {
                "name": "readOnly",
                "source": "readOnly",
                "type": "TEXT"
            },
            {
                "name": "singleProjectCode",
                "source": "singleProjectCode",
                "type": "TEXT"
            },
            {
                "name": "singleProjectName",
                "source": "singleProjectName",
                "type": "TEXT"
            },
            {
                "name": "traceId",
                "source": "traceId",
                "type": "TEXT"
            },
            {
                "name": "updateTime",
                "source": "updateTime",
                "type": "TEXT"
            },
            {
                "name": "updater",
                "source": "updater",
                "type": "TEXT"
            },
            {
                "name": "updaterId",
                "source": "updaterId",
                "type": "TEXT"
            },
            {
                "name": "workSiteName",
                "source": "workSiteName",
                "type": "TEXT"
            }
        ],
        "dataset_key": "dataset_5f5a4fcf",
        "key_candidates": [
            "id",
            "prjCode",
            "singleProjectCode",
            "biddingSectionCode",
            "prjCode+singleProjectCode+biddingSectionCode"
        ],
        "page_name": "作业部位管理",
        "parent_record_path": "raw_event",
        "partition_field": "prjCode",
        "partition_key": "prjCode",
        "plugin_id": "dcp-dataset-5f5a4fcf",
        "record_path": "raw_event.children[]",
        "record_type": "worksite_substation:raw_event.children[]",
        "table": "canonical_p003_page_5f5a4fcf__worksite_substation__raw_event_children_items"
    },
    {
        "api_name": "worksite_tower",
        "api_path": "/apit/ebuild2-domain-security-risk/v1/worksite/queryTowerPage",
        "columns": [
            {
                "name": "address",
                "source": "address",
                "type": "TEXT"
            },
            {
                "name": "biddingSectionCode",
                "source": "biddingSectionCode",
                "type": "TEXT"
            },
            {
                "name": "biddingSectionName",
                "source": "biddingSectionName",
                "type": "TEXT"
            },
            {
                "name": "borrowedFlag",
                "source": "borrowedFlag",
                "type": "INTEGER"
            },
            {
                "name": "centerPileElevation",
                "source": "centerPileElevation",
                "type": "REAL"
            },
            {
                "name": "circuitQuantity",
                "source": "circuitQuantity",
                "type": "TEXT"
            },
            {
                "name": "circuitQuantityText",
                "source": "circuitQuantityText",
                "type": "TEXT"
            },
            {
                "name": "county",
                "source": "county",
                "type": "TEXT"
            },
            {
                "name": "cover4gFlag",
                "source": "cover4gFlag",
                "type": "INTEGER"
            },
            {
                "name": "designChangeNo",
                "source": "designChangeNo",
                "type": "TEXT"
            },
            {
                "name": "dismantleFlag",
                "source": "dismantleFlag",
                "type": "INTEGER"
            },
            {
                "name": "eastCoordinate",
                "source": "eastCoordinate",
                "type": "TEXT"
            },
            {
                "name": "extra",
                "source": "extra",
                "type": "TEXT"
            },
            {
                "name": "generalDesignFlag",
                "source": "generalDesignFlag",
                "type": "TEXT"
            },
            {
                "name": "geology",
                "source": "geology",
                "type": "TEXT"
            },
            {
                "name": "groundThingName",
                "source": "groundThingName",
                "type": "TEXT"
            },
            {
                "name": "id",
                "source": "id",
                "type": "TEXT"
            },
            {
                "name": "latitude",
                "source": "latitude",
                "type": "TEXT"
            },
            {
                "name": "longitude",
                "source": "longitude",
                "type": "TEXT"
            },
            {
                "name": "majorCrossingFlag",
                "source": "majorCrossingFlag",
                "type": "TEXT"
            },
            {
                "name": "moduleNo",
                "source": "moduleNo",
                "type": "TEXT"
            },
            {
                "name": "nominalHeight",
                "source": "nominalHeight",
                "type": "REAL"
            },
            {
                "name": "northCoordinate",
                "source": "northCoordinate",
                "type": "TEXT"
            },
            {
                "name": "prjCode",
                "source": "prjCode",
                "type": "TEXT"
            },
            {
                "name": "prjName",
                "source": "prjName",
                "type": "TEXT"
            },
            {
                "name": "remark",
                "source": "remark",
                "type": "TEXT"
            },
            {
                "name": "representativeSpan",
                "source": "representativeSpan",
                "type": "TEXT"
            },
            {
                "name": "rotationDegree",
                "source": "rotationDegree",
                "type": "TEXT"
            },
            {
                "name": "runTowerCode",
                "source": "runTowerCode",
                "type": "TEXT"
            },
            {
                "name": "sectionDividePointFlag",
                "source": "sectionDividePointFlag",
                "type": "INTEGER"
            },
            {
                "name": "dcp_select",
                "source": "select",
                "type": "TEXT"
            },
            {
                "name": "singleProjectCode",
                "source": "singleProjectCode",
                "type": "TEXT"
            },
            {
                "name": "singleProjectName",
                "source": "singleProjectName",
                "type": "TEXT"
            },
            {
                "name": "slope",
                "source": "slope",
                "type": "TEXT"
            },
            {
                "name": "span",
                "source": "span",
                "type": "TEXT"
            },
            {
                "name": "stentFlag",
                "source": "stentFlag",
                "type": "INTEGER"
            },
            {
                "name": "tensionSectionLength",
                "source": "tensionSectionLength",
                "type": "TEXT"
            },
            {
                "name": "tensionTowerFlag",
                "source": "tensionTowerFlag",
                "type": "INTEGER"
            },
            {
                "name": "topography",
                "source": "topography",
                "type": "INTEGER"
            },
            {
                "name": "towerCuircuitNumber",
                "source": "towerCuircuitNumber",
                "type": "TEXT"
            },
            {
                "name": "towerCuircuitNumberText",
                "source": "towerCuircuitNumberText",
                "type": "TEXT"
            },
            {
                "name": "towerFullHeight",
                "source": "towerFullHeight",
                "type": "REAL"
            },
            {
                "name": "towerLegBaseformFirst",
                "source": "towerLegBaseformFirst",
                "type": "TEXT"
            },
            {
                "name": "towerLegBaseformFourth",
                "source": "towerLegBaseformFourth",
                "type": "TEXT"
            },
            {
                "name": "towerLegBaseformSecond",
                "source": "towerLegBaseformSecond",
                "type": "TEXT"
            },
            {
                "name": "towerLegBaseformThird",
                "source": "towerLegBaseformThird",
                "type": "TEXT"
            },
            {
                "name": "towerLegMaxDepthFirst",
                "source": "towerLegMaxDepthFirst",
                "type": "TEXT"
            },
            {
                "name": "towerLegMaxDepthFourth",
                "source": "towerLegMaxDepthFourth",
                "type": "TEXT"
            },
            {
                "name": "towerLegMaxDepthSecond",
                "source": "towerLegMaxDepthSecond",
                "type": "TEXT"
            },
            {
                "name": "towerLegMaxDepthThird",
                "source": "towerLegMaxDepthThird",
                "type": "TEXT"
            },
            {
                "name": "towerNo",
                "source": "towerNo",
                "type": "TEXT"
            },
            {
                "name": "towerSequenceNo",
                "source": "towerSequenceNo",
                "type": "INTEGER"
            },
            {
                "name": "towerStructure",
                "source": "towerStructure",
                "type": "TEXT"
            },
            {
                "name": "towerType",
                "source": "towerType",
                "type": "TEXT"
            },
            {
                "name": "towerTypeNo",
                "source": "towerTypeNo",
                "type": "TEXT"
            },
            {
                "name": "towerWeight",
                "source": "towerWeight",
                "type": "REAL"
            },
            {
                "name": "town",
                "source": "town",
                "type": "TEXT"
            },
            {
                "name": "traceId",
                "source": "traceId",
                "type": "TEXT"
            },
            {
                "name": "type",
                "source": "type",
                "type": "INTEGER"
            },
            {
                "name": "upstreamTowerNo",
                "source": "upstreamTowerNo",
                "type": "TEXT"
            },
            {
                "name": "village",
                "source": "village",
                "type": "TEXT"
            }
        ],
        "dataset_key": "dataset_5f5a4fcf",
        "key_candidates": [
            "id",
            "prjCode",
            "singleProjectCode",
            "biddingSectionCode",
            "towerNo",
            "prjCode+singleProjectCode+biddingSectionCode+towerNo"
        ],
        "page_name": "作业部位管理",
        "parent_record_path": null,
        "partition_field": "prjCode",
        "partition_key": "prjCode",
        "plugin_id": "dcp-dataset-5f5a4fcf",
        "record_path": "raw_event",
        "record_type": "worksite_tower:raw_event",
        "table": "canonical_p003_page_5f5a4fcf__worksite_tower__raw_event"
    },
    {
        "api_name": "blackout_execution",
        "api_path": "/apit/ebuild2-domain-plan-foundation/v1/blackoutPlanExecution/queryBlackoutExecutionPage",
        "columns": [
            {
                "name": "auditStatus",
                "source": "auditStatus",
                "type": "INTEGER"
            },
            {
                "name": "blackoutExecutionCount",
                "source": "blackoutExecutionCount",
                "type": "INTEGER"
            },
            {
                "name": "blackoutName",
                "source": "blackoutName",
                "type": "TEXT"
            },
            {
                "name": "buttonFlag",
                "source": "buttonFlag",
                "type": "INTEGER"
            },
            {
                "name": "id",
                "source": "id",
                "type": "TEXT"
            },
            {
                "name": "monthBlackoutPrjCount",
                "source": "monthBlackoutPrjCount",
                "type": "TEXT"
            },
            {
                "name": "planAdd",
                "source": "planAdd",
                "type": "INTEGER"
            },
            {
                "name": "planBefore",
                "source": "planBefore",
                "type": "INTEGER"
            },
            {
                "name": "planCancel",
                "source": "planCancel",
                "type": "INTEGER"
            },
            {
                "name": "planDelay",
                "source": "planDelay",
                "type": "INTEGER"
            },
            {
                "name": "planDelayToCurrentMonth",
                "source": "planDelayToCurrentMonth",
                "type": "INTEGER"
            },
            {
                "name": "planMonth",
                "source": "planMonth",
                "type": "INTEGER"
            },
            {
                "name": "planNormal",
                "source": "planNormal",
                "type": "INTEGER"
            },
            {
                "name": "planYear",
                "source": "planYear",
                "type": "TEXT"
            },
            {
                "name": "provinceCode",
                "source": "provinceCode",
                "type": "TEXT"
            },
            {
                "name": "provinceName",
                "source": "provinceName",
                "type": "TEXT"
            },
            {
                "name": "provinceReportList",
                "source": "provinceReportList",
                "type": "TEXT"
            },
            {
                "name": "releaseFlag",
                "source": "releaseFlag",
                "type": "INTEGER"
            },
            {
                "name": "reportStatus",
                "source": "reportStatus",
                "type": "INTEGER"
            },
            {
                "name": "reportUserId",
                "source": "reportUserId",
                "type": "TEXT"
            },
            {
                "name": "reportUserName",
                "source": "reportUserName",
                "type": "TEXT"
            },
            {
                "name": "returnReason",
                "source": "returnReason",
                "type": "TEXT"
            },
            {
                "name": "submitTime",
                "source": "submitTime",
                "type": "TEXT"
            },
            {
                "name": "weaveUserId",
                "source": "weaveUserId",
                "type": "TEXT"
            },
            {
                "name": "weaveUserName",
                "source": "weaveUserName",
                "type": "TEXT"
            }
        ],
        "dataset_key": "dataset_7abd177c",
        "key_candidates": [
            "id"
        ],
        "page_name": "停电计划执行上报与查看",
        "parent_record_path": null,
        "partition_field": null,
        "partition_key": null,
        "plugin_id": "dcp-dataset-7abd177c",
        "record_path": "raw_event",
        "record_type": "blackout_execution:raw_event",
        "table": "canonical_p004_page_7abd177c__blackout_execution__raw_event"
    },
    {
        "api_name": "blackout_execution",
        "api_path": "/apit/ebuild2-domain-plan-foundation/v1/blackoutPlanExecution/queryBlackoutExecutionPage",
        "columns": [
            {
                "name": "auditUserName",
                "source": "auditUserName",
                "type": "TEXT"
            },
            {
                "name": "planMonth",
                "source": "planMonth",
                "type": "INTEGER"
            },
            {
                "name": "planYear",
                "source": "planYear",
                "type": "TEXT"
            },
            {
                "name": "provinceCode",
                "source": "provinceCode",
                "type": "TEXT"
            },
            {
                "name": "taskId",
                "source": "taskId",
                "type": "TEXT"
            },
            {
                "name": "weaveUserName",
                "source": "weaveUserName",
                "type": "TEXT"
            }
        ],
        "dataset_key": "dataset_7abd177c",
        "key_candidates": [
            "source_record_key+record_path"
        ],
        "page_name": "停电计划执行上报与查看",
        "parent_record_path": "raw_event",
        "partition_field": null,
        "partition_key": null,
        "plugin_id": "dcp-dataset-7abd177c",
        "record_path": "raw_event.provinceReportList[]",
        "record_type": "blackout_execution:raw_event.provinceReportList[]",
        "table": "canonical_p004_page_7abd177c__blackout_execution__raw_event_provincereportlist_items"
    },
    {
        "api_name": "blackout_execution_details",
        "api_path": "/apit/ebuild2-domain-plan-foundation/v1/blackoutPlanExecution/queryBlackoutExecutionDetails",
        "columns": [
            {
                "name": "actualBlackoutEndDate",
                "source": "actualBlackoutEndDate",
                "type": "TEXT"
            },
            {
                "name": "actualBlackoutStartDate",
                "source": "actualBlackoutStartDate",
                "type": "TEXT"
            },
            {
                "name": "blackoutCode",
                "source": "blackoutCode",
                "type": "TEXT"
            },
            {
                "name": "blackoutId",
                "source": "blackoutId",
                "type": "TEXT"
            },
            {
                "name": "blackoutPlanStatus",
                "source": "blackoutPlanStatus",
                "type": "INTEGER"
            },
            {
                "name": "blackoutPlanStatusName",
                "source": "blackoutPlanStatusName",
                "type": "TEXT"
            },
            {
                "name": "constructionStatus",
                "source": "constructionStatus",
                "type": "TEXT"
            },
            {
                "name": "declarationDays",
                "source": "declarationDays",
                "type": "TEXT"
            },
            {
                "name": "equipmentName",
                "source": "equipmentName",
                "type": "TEXT"
            },
            {
                "name": "extra",
                "source": "extra",
                "type": "TEXT"
            },
            {
                "name": "id",
                "source": "id",
                "type": "TEXT"
            },
            {
                "name": "overhaulId",
                "source": "overhaulId",
                "type": "TEXT"
            },
            {
                "name": "planBlackoutEndDate",
                "source": "planBlackoutEndDate",
                "type": "TEXT"
            },
            {
                "name": "planBlackoutStartDate",
                "source": "planBlackoutStartDate",
                "type": "TEXT"
            },
            {
                "name": "planFlag",
                "source": "planFlag",
                "type": "INTEGER"
            },
            {
                "name": "planMonth",
                "source": "planMonth",
                "type": "INTEGER"
            },
            {
                "name": "planYear",
                "source": "planYear",
                "type": "TEXT"
            },
            {
                "name": "prjCode",
                "source": "prjCode",
                "type": "TEXT"
            },
            {
                "name": "prjName",
                "source": "prjName",
                "type": "TEXT"
            },
            {
                "name": "projectOperationPlanDate",
                "source": "projectOperationPlanDate",
                "type": "TEXT"
            },
            {
                "name": "provinceCode",
                "source": "provinceCode",
                "type": "TEXT"
            },
            {
                "name": "provinceName",
                "source": "provinceName",
                "type": "TEXT"
            },
            {
                "name": "singleProjectCode",
                "source": "singleProjectCode",
                "type": "TEXT"
            },
            {
                "name": "singleProjectName",
                "source": "singleProjectName",
                "type": "TEXT"
            },
            {
                "name": "traceId",
                "source": "traceId",
                "type": "TEXT"
            },
            {
                "name": "unDeclaredReason",
                "source": "unDeclaredReason",
                "type": "TEXT"
            },
            {
                "name": "unExecutionReason",
                "source": "unExecutionReason",
                "type": "TEXT"
            },
            {
                "name": "unExecutionReasonName",
                "source": "unExecutionReasonName",
                "type": "TEXT"
            },
            {
                "name": "voltageLevel",
                "source": "voltageLevel",
                "type": "TEXT"
            }
        ],
        "dataset_key": "dataset_7abd177c",
        "key_candidates": [
            "id",
            "prjCode",
            "singleProjectCode",
            "prjCode+singleProjectCode"
        ],
        "page_name": "停电计划执行上报与查看",
        "parent_record_path": null,
        "partition_field": "prjCode",
        "partition_key": "prjCode",
        "plugin_id": "dcp-dataset-7abd177c",
        "record_path": "raw_event",
        "record_type": "blackout_execution_details:raw_event",
        "table": "canonical_p004_page_7abd177c__blackout_execution_details__raw_event"
    },
    {
        "api_name": "section_single_projects",
        "api_path": "/apit/ebuild2-common-project-digitization/section/getSingleProject",
        "columns": [
            {
                "name": "positionCode",
                "source": "positionCode",
                "type": "TEXT"
            },
            {
                "name": "positionName",
                "source": "positionName",
                "type": "TEXT"
            },
            {
                "name": "singleProjectCode",
                "source": "singleProjectCode",
                "type": "TEXT"
            },
            {
                "name": "singleProjectName",
                "source": "singleProjectName",
                "type": "TEXT"
            },
            {
                "name": "singleProjectType",
                "source": "singleProjectType",
                "type": "INTEGER"
            }
        ],
        "dataset_key": "dataset_18d113ac",
        "key_candidates": [
            "singleProjectCode"
        ],
        "page_name": "区段划分",
        "parent_record_path": null,
        "partition_field": "singleProjectCode",
        "partition_key": "singleProjectCode",
        "plugin_id": "dcp-dataset-18d113ac",
        "record_path": "raw_event",
        "record_type": "section_single_projects:raw_event",
        "table": "canonical_p005_page_18d113ac__section_single_projects__raw_event"
    },
    {
        "api_name": "section_single_projects",
        "api_path": "/apit/ebuild2-common-project-digitization/section/getSingleProject",
        "columns": [
            {
                "name": "biddingSectionCode",
                "source": "biddingSectionCode",
                "type": "TEXT"
            },
            {
                "name": "biddingSectionName",
                "source": "biddingSectionName",
                "type": "TEXT"
            }
        ],
        "dataset_key": "dataset_18d113ac",
        "key_candidates": [
            "biddingSectionCode"
        ],
        "page_name": "区段划分",
        "parent_record_path": "raw_event",
        "partition_field": "biddingSectionCode",
        "partition_key": "biddingSectionCode",
        "plugin_id": "dcp-dataset-18d113ac",
        "record_path": "raw_event.sectList[]",
        "record_type": "section_single_projects:raw_event.sectList[]",
        "table": "canonical_p005_page_18d113ac__section_single_projects__raw_event_sectlist_items"
    },
    {
        "api_name": "single_project_maintenance",
        "api_path": "/apit/ebuild2-domain-project-form/v1/sinDivide/queryProjectList",
        "columns": [
            {
                "name": "actualCommencementDate",
                "source": "actualCommencementDate",
                "type": "TEXT"
            },
            {
                "name": "actualCommissioningDate",
                "source": "actualCommissioningDate",
                "type": "TEXT"
            },
            {
                "name": "actualComplDate",
                "source": "actualComplDate",
                "type": "TEXT"
            },
            {
                "name": "apprFileNo",
                "source": "apprFileNo",
                "type": "TEXT"
            },
            {
                "name": "buildUnitCode",
                "source": "buildUnitCode",
                "type": "TEXT"
            },
            {
                "name": "buildUnitName",
                "source": "buildUnitName",
                "type": "TEXT"
            },
            {
                "name": "constrAddress",
                "source": "constrAddress",
                "type": "TEXT"
            },
            {
                "name": "constrNature",
                "source": "constrNature",
                "type": "INTEGER"
            },
            {
                "name": "constrNatureName",
                "source": "constrNatureName",
                "type": "TEXT"
            },
            {
                "name": "constrTransformerCapacity",
                "source": "constrTransformerCapacity",
                "type": "REAL"
            },
            {
                "name": "constructionCategory",
                "source": "constructionCategory",
                "type": "INTEGER"
            },
            {
                "name": "constructionCategoryName",
                "source": "constructionCategoryName",
                "type": "TEXT"
            },
            {
                "name": "constructionLineLength",
                "source": "constructionLineLength",
                "type": "REAL"
            },
            {
                "name": "constructionStatus",
                "source": "constructionStatus",
                "type": "INTEGER"
            },
            {
                "name": "createTime",
                "source": "createTime",
                "type": "TEXT"
            },
            {
                "name": "createrId",
                "source": "createrId",
                "type": "TEXT"
            },
            {
                "name": "deleteButton",
                "source": "deleteButton",
                "type": "TEXT"
            },
            {
                "name": "deleteFlag",
                "source": "deleteFlag",
                "type": "INTEGER"
            },
            {
                "name": "deptStatus",
                "source": "deptStatus",
                "type": "TEXT"
            },
            {
                "name": "earlierStageFile",
                "source": "earlierStageFile",
                "type": "TEXT"
            },
            {
                "name": "existsFlag",
                "source": "existsFlag",
                "type": "TEXT"
            },
            {
                "name": "extra",
                "source": "extra",
                "type": "TEXT"
            },
            {
                "name": "feaDinvest",
                "source": "feaDinvest",
                "type": "REAL"
            },
            {
                "name": "feaLineLength",
                "source": "feaLineLength",
                "type": "REAL"
            },
            {
                "name": "feaSinvest",
                "source": "feaSinvest",
                "type": "REAL"
            },
            {
                "name": "feasTransCapacity",
                "source": "feasTransCapacity",
                "type": "REAL"
            },
            {
                "name": "id",
                "source": "id",
                "type": "TEXT"
            },
            {
                "name": "lineQuantity",
                "source": "lineQuantity",
                "type": "INTEGER"
            },
            {
                "name": "locationArea",
                "source": "locationArea",
                "type": "TEXT"
            },
            {
                "name": "locationAreaName",
                "source": "locationAreaName",
                "type": "TEXT"
            },
            {
                "name": "locationMunicipality",
                "source": "locationMunicipality",
                "type": "TEXT"
            },
            {
                "name": "locationMunicipalityName",
                "source": "locationMunicipalityName",
                "type": "TEXT"
            },
            {
                "name": "locationProvince",
                "source": "locationProvince",
                "type": "TEXT"
            },
            {
                "name": "locationProvinceName",
                "source": "locationProvinceName",
                "type": "TEXT"
            },
            {
                "name": "mainTransformerQuantity",
                "source": "mainTransformerQuantity",
                "type": "INTEGER"
            },
            {
                "name": "nonConstrDepartmentImpl",
                "source": "nonConstrDepartmentImpl",
                "type": "INTEGER"
            },
            {
                "name": "num",
                "source": "num",
                "type": "TEXT"
            },
            {
                "name": "planComplDate",
                "source": "planComplDate",
                "type": "TEXT"
            },
            {
                "name": "plannedCommencementDate",
                "source": "plannedCommencementDate",
                "type": "TEXT"
            },
            {
                "name": "plannedCommissioningDate",
                "source": "plannedCommissioningDate",
                "type": "TEXT"
            },
            {
                "name": "prjCode",
                "source": "prjCode",
                "type": "TEXT"
            },
            {
                "name": "prjManageMode",
                "source": "prjManageMode",
                "type": "INTEGER"
            },
            {
                "name": "prjName",
                "source": "prjName",
                "type": "TEXT"
            },
            {
                "name": "prjSource",
                "source": "prjSource",
                "type": "INTEGER"
            },
            {
                "name": "prjStatus",
                "source": "prjStatus",
                "type": "INTEGER"
            },
            {
                "name": "prodTransCapacity",
                "source": "prodTransCapacity",
                "type": "TEXT"
            },
            {
                "name": "productionLineLength",
                "source": "productionLineLength",
                "type": "TEXT"
            },
            {
                "name": "projectApprovalDocumentNo",
                "source": "projectApprovalDocumentNo",
                "type": "TEXT"
            },
            {
                "name": "projectDateList",
                "source": "projectDateList",
                "type": "TEXT"
            },
            {
                "name": "projectType",
                "source": "projectType",
                "type": "INTEGER"
            },
            {
                "name": "projectTypeName",
                "source": "projectTypeName",
                "type": "TEXT"
            },
            {
                "name": "provinceCode",
                "source": "provinceCode",
                "type": "TEXT"
            },
            {
                "name": "provinceName",
                "source": "provinceName",
                "type": "TEXT"
            },
            {
                "name": "pushStatus",
                "source": "pushStatus",
                "type": "INTEGER"
            },
            {
                "name": "reserveButton",
                "source": "reserveButton",
                "type": "INTEGER"
            },
            {
                "name": "same",
                "source": "same",
                "type": "TEXT"
            },
            {
                "name": "sinDivideStatus",
                "source": "sinDivideStatus",
                "type": "TEXT"
            },
            {
                "name": "sinList",
                "source": "sinList",
                "type": "TEXT"
            },
            {
                "name": "traceId",
                "source": "traceId",
                "type": "TEXT"
            },
            {
                "name": "updateTime",
                "source": "updateTime",
                "type": "TEXT"
            },
            {
                "name": "updaterId",
                "source": "updaterId",
                "type": "TEXT"
            },
            {
                "name": "voltageLevel",
                "source": "voltageLevel",
                "type": "TEXT"
            },
            {
                "name": "voltageLevelName",
                "source": "voltageLevelName",
                "type": "TEXT"
            }
        ],
        "dataset_key": "dataset_814e0a01",
        "key_candidates": [
            "id",
            "prjCode"
        ],
        "page_name": "单项信息维护",
        "parent_record_path": null,
        "partition_field": "prjCode",
        "partition_key": "prjCode",
        "plugin_id": "dcp-dataset-814e0a01",
        "record_path": "raw_event",
        "record_type": "single_project_maintenance:raw_event",
        "table": "canonical_p006_page_814e0a01__single_project_maintenance__raw_event"
    },
    {
        "api_name": "substation_single_projects",
        "api_path": "/apit/ebuild2-domain-project-stage/v1/substationCoordinates/querySubSinPrjInfo",
        "columns": [
            {
                "name": "conOperate",
                "source": "conOperate",
                "type": "INTEGER"
            },
            {
                "name": "singleProjectCode",
                "source": "singleProjectCode",
                "type": "TEXT"
            },
            {
                "name": "singleProjectName",
                "source": "singleProjectName",
                "type": "TEXT"
            }
        ],
        "dataset_key": "dataset_9d439395",
        "key_candidates": [
            "singleProjectCode"
        ],
        "page_name": "变电站坐标",
        "parent_record_path": null,
        "partition_field": "singleProjectCode",
        "partition_key": "singleProjectCode",
        "plugin_id": "dcp-dataset-9d439395",
        "record_path": "raw_event",
        "record_type": "substation_single_projects:raw_event",
        "table": "canonical_p007_page_9d439395__substation_single_projects__raw_event"
    },
    {
        "api_name": "production_startup_info",
        "api_path": "/apit/ebuild2-domain-project-stage/v1/production/getPrivateProduction",
        "columns": [
            {
                "name": "actualCommencementDate",
                "source": "actualCommencementDate",
                "type": "TEXT"
            },
            {
                "name": "actualCommissioningDate",
                "source": "actualCommissioningDate",
                "type": "TEXT"
            },
            {
                "name": "constrTransformerCapacity",
                "source": "constrTransformerCapacity",
                "type": "REAL"
            },
            {
                "name": "constructionLineLength",
                "source": "constructionLineLength",
                "type": "TEXT"
            },
            {
                "name": "extra",
                "source": "extra",
                "type": "TEXT"
            },
            {
                "name": "id",
                "source": "id",
                "type": "TEXT"
            },
            {
                "name": "plannedCommissioningDate",
                "source": "plannedCommissioningDate",
                "type": "TEXT"
            },
            {
                "name": "prjCode",
                "source": "prjCode",
                "type": "TEXT"
            },
            {
                "name": "prjName",
                "source": "prjName",
                "type": "TEXT"
            },
            {
                "name": "proProductionSwitch",
                "source": "proProductionSwitch",
                "type": "TEXT"
            },
            {
                "name": "prodTransCapacity",
                "source": "prodTransCapacity",
                "type": "REAL"
            },
            {
                "name": "productionLineLength",
                "source": "productionLineLength",
                "type": "INTEGER"
            },
            {
                "name": "projectProductionFlag",
                "source": "projectProductionFlag",
                "type": "INTEGER"
            },
            {
                "name": "provinceCode",
                "source": "provinceCode",
                "type": "TEXT"
            },
            {
                "name": "testRunDate",
                "source": "testRunDate",
                "type": "TEXT"
            },
            {
                "name": "traceId",
                "source": "traceId",
                "type": "TEXT"
            },
            {
                "name": "voltageLevel",
                "source": "voltageLevel",
                "type": "TEXT"
            },
            {
                "name": "voltageLevelText",
                "source": "voltageLevelText",
                "type": "TEXT"
            }
        ],
        "dataset_key": "dataset_2d518fa0",
        "key_candidates": [
            "id",
            "prjCode"
        ],
        "page_name": "启动投运",
        "parent_record_path": null,
        "partition_field": "prjCode",
        "partition_key": "prjCode",
        "plugin_id": "dcp-dataset-2d518fa0",
        "record_path": "raw_event",
        "record_type": "production_startup_info:raw_event",
        "table": "canonical_p008_page_2d518fa0__production_startup_info__raw_event"
    },
    {
        "api_name": "production_startup_info",
        "api_path": "/apit/ebuild2-domain-project-stage/v1/production/getPrivateProduction",
        "columns": [
            {
                "name": "actualCommencementDate",
                "source": "actualCommencementDate",
                "type": "TEXT"
            },
            {
                "name": "actualCommissioningDate",
                "source": "actualCommissioningDate",
                "type": "TEXT"
            },
            {
                "name": "approvalStatus",
                "source": "approvalStatus",
                "type": "INTEGER"
            },
            {
                "name": "bpmId",
                "source": "bpmId",
                "type": "TEXT"
            },
            {
                "name": "constructionStatus",
                "source": "constructionStatus",
                "type": "TEXT"
            },
            {
                "name": "extra",
                "source": "extra",
                "type": "TEXT"
            },
            {
                "name": "id",
                "source": "id",
                "type": "TEXT"
            },
            {
                "name": "operateFlag",
                "source": "operateFlag",
                "type": "TEXT"
            },
            {
                "name": "planProdLineLength",
                "source": "planProdLineLength",
                "type": "TEXT"
            },
            {
                "name": "planProdTransCapacity",
                "source": "planProdTransCapacity",
                "type": "TEXT"
            },
            {
                "name": "prodTransCapacity",
                "source": "prodTransCapacity",
                "type": "REAL"
            },
            {
                "name": "productionDate",
                "source": "productionDate",
                "type": "TEXT"
            },
            {
                "name": "productionLineLength",
                "source": "productionLineLength",
                "type": "TEXT"
            },
            {
                "name": "productionStatus",
                "source": "productionStatus",
                "type": "INTEGER"
            },
            {
                "name": "provinceCode",
                "source": "provinceCode",
                "type": "TEXT"
            },
            {
                "name": "returnReason",
                "source": "returnReason",
                "type": "TEXT"
            },
            {
                "name": "singleProjectCode",
                "source": "singleProjectCode",
                "type": "TEXT"
            },
            {
                "name": "singleProjectDetailsType",
                "source": "singleProjectDetailsType",
                "type": "INTEGER"
            },
            {
                "name": "singleProjectName",
                "source": "singleProjectName",
                "type": "TEXT"
            },
            {
                "name": "singleProjectType",
                "source": "singleProjectType",
                "type": "TEXT"
            },
            {
                "name": "traceId",
                "source": "traceId",
                "type": "TEXT"
            }
        ],
        "dataset_key": "dataset_2d518fa0",
        "key_candidates": [
            "id",
            "singleProjectCode"
        ],
        "page_name": "启动投运",
        "parent_record_path": "raw_event",
        "partition_field": "singleProjectCode",
        "partition_key": "singleProjectCode",
        "plugin_id": "dcp-dataset-2d518fa0",
        "record_path": "raw_event.singleProjectProductionDTOList[]",
        "record_type": "production_startup_info:raw_event.singleProjectProductionDTOList[]",
        "table": "canonical_p008_page_2d518fa0__production_startup_info__raw_event_singleprojectproductiondtolist_items"
    },
    {
        "api_name": "production_startup_info",
        "api_path": "/apit/ebuild2-domain-project-stage/v1/production/getPrivateProduction",
        "columns": [
            {
                "name": "extra",
                "source": "extra",
                "type": "TEXT"
            },
            {
                "name": "fileId",
                "source": "fileId",
                "type": "TEXT"
            },
            {
                "name": "fileName",
                "source": "fileName",
                "type": "TEXT"
            },
            {
                "name": "fileTypeCode",
                "source": "fileTypeCode",
                "type": "INTEGER"
            },
            {
                "name": "id",
                "source": "id",
                "type": "TEXT"
            },
            {
                "name": "traceId",
                "source": "traceId",
                "type": "TEXT"
            },
            {
                "name": "uploadId",
                "source": "uploadId",
                "type": "TEXT"
            },
            {
                "name": "uploadName",
                "source": "uploadName",
                "type": "TEXT"
            },
            {
                "name": "uploadTime",
                "source": "uploadTime",
                "type": "TEXT"
            }
        ],
        "dataset_key": "dataset_2d518fa0",
        "key_candidates": [
            "id"
        ],
        "page_name": "启动投运",
        "parent_record_path": "raw_event",
        "partition_field": null,
        "partition_key": null,
        "plugin_id": "dcp-dataset-2d518fa0",
        "record_path": "raw_event.fileDTOList[]",
        "record_type": "production_startup_info:raw_event.fileDTOList[]",
        "table": "canonical_p008_page_2d518fa0__production_startup_info__raw_event_filedtolist_items"
    },
    {
        "api_name": "startup_committee",
        "api_path": "/apit/ebuild2-domain-project-stage/v1/openingCommittee/getOpeningCommittee",
        "columns": [
            {
                "name": "buildUnitCode",
                "source": "buildUnitCode",
                "type": "TEXT"
            },
            {
                "name": "canUpload",
                "source": "canUpload",
                "type": "INTEGER"
            },
            {
                "name": "constrTransformerCapacity",
                "source": "constrTransformerCapacity",
                "type": "REAL"
            },
            {
                "name": "constructionLineLength",
                "source": "constructionLineLength",
                "type": "TEXT"
            },
            {
                "name": "establishmentDate",
                "source": "establishmentDate",
                "type": "TEXT"
            },
            {
                "name": "extra",
                "source": "extra",
                "type": "TEXT"
            },
            {
                "name": "id",
                "source": "id",
                "type": "TEXT"
            },
            {
                "name": "operationFlag",
                "source": "operationFlag",
                "type": "INTEGER"
            },
            {
                "name": "prjCode",
                "source": "prjCode",
                "type": "TEXT"
            },
            {
                "name": "prjName",
                "source": "prjName",
                "type": "TEXT"
            },
            {
                "name": "provinceCode",
                "source": "provinceCode",
                "type": "TEXT"
            },
            {
                "name": "traceId",
                "source": "traceId",
                "type": "TEXT"
            },
            {
                "name": "voltageLevel",
                "source": "voltageLevel",
                "type": "TEXT"
            },
            {
                "name": "voltageLevelText",
                "source": "voltageLevelText",
                "type": "TEXT"
            }
        ],
        "dataset_key": "dataset_eaa452c4",
        "key_candidates": [
            "id",
            "prjCode"
        ],
        "page_name": "启委会管理",
        "parent_record_path": null,
        "partition_field": "prjCode",
        "partition_key": "prjCode",
        "plugin_id": "dcp-dataset-eaa452c4",
        "record_path": "raw_event",
        "record_type": "startup_committee:raw_event",
        "table": "canonical_p009_page_eaa452c4__startup_committee__raw_event"
    },
    {
        "api_name": "startup_committee",
        "api_path": "/apit/ebuild2-domain-project-stage/v1/openingCommittee/getOpeningCommittee",
        "columns": [
            {
                "name": "committeeId",
                "source": "committeeId",
                "type": "TEXT"
            },
            {
                "name": "extra",
                "source": "extra",
                "type": "TEXT"
            },
            {
                "name": "fileId",
                "source": "fileId",
                "type": "TEXT"
            },
            {
                "name": "fileTypeCode",
                "source": "fileTypeCode",
                "type": "INTEGER"
            },
            {
                "name": "fileTypeName",
                "source": "fileTypeName",
                "type": "TEXT"
            },
            {
                "name": "id",
                "source": "id",
                "type": "TEXT"
            },
            {
                "name": "traceId",
                "source": "traceId",
                "type": "TEXT"
            },
            {
                "name": "uploadId",
                "source": "uploadId",
                "type": "TEXT"
            },
            {
                "name": "uploadName",
                "source": "uploadName",
                "type": "TEXT"
            },
            {
                "name": "uploadTime",
                "source": "uploadTime",
                "type": "TEXT"
            }
        ],
        "dataset_key": "dataset_eaa452c4",
        "key_candidates": [
            "id"
        ],
        "page_name": "启委会管理",
        "parent_record_path": "raw_event",
        "partition_field": null,
        "partition_key": null,
        "plugin_id": "dcp-dataset-eaa452c4",
        "record_path": "raw_event.fileDTOList[]",
        "record_type": "startup_committee:raw_event.fileDTOList[]",
        "table": "canonical_p009_page_eaa452c4__startup_committee__raw_event_filedtolist_items"
    },
    {
        "api_name": "startup_committee",
        "api_path": "/apit/ebuild2-domain-project-stage/v1/openingCommittee/getOpeningCommittee",
        "columns": [
            {
                "name": "extra",
                "source": "extra",
                "type": "TEXT"
            },
            {
                "name": "fileDTOList",
                "source": "fileDTOList",
                "type": "TEXT"
            },
            {
                "name": "fileType",
                "source": "fileType",
                "type": "INTEGER"
            },
            {
                "name": "fileTypeName",
                "source": "fileTypeName",
                "type": "TEXT"
            },
            {
                "name": "id",
                "source": "id",
                "type": "INTEGER"
            },
            {
                "name": "traceId",
                "source": "traceId",
                "type": "TEXT"
            }
        ],
        "dataset_key": "dataset_eaa452c4",
        "key_candidates": [
            "id"
        ],
        "page_name": "启委会管理",
        "parent_record_path": "raw_event",
        "partition_field": null,
        "partition_key": null,
        "plugin_id": "dcp-dataset-eaa452c4",
        "record_path": "raw_event.fileVOList[]",
        "record_type": "startup_committee:raw_event.fileVOList[]",
        "table": "canonical_p009_page_eaa452c4__startup_committee__raw_event_filevolist_items"
    },
    {
        "api_name": "startup_committee",
        "api_path": "/apit/ebuild2-domain-project-stage/v1/openingCommittee/getOpeningCommittee",
        "columns": [
            {
                "name": "committeeId",
                "source": "committeeId",
                "type": "TEXT"
            },
            {
                "name": "extra",
                "source": "extra",
                "type": "TEXT"
            },
            {
                "name": "fileId",
                "source": "fileId",
                "type": "TEXT"
            },
            {
                "name": "fileTypeCode",
                "source": "fileTypeCode",
                "type": "INTEGER"
            },
            {
                "name": "fileTypeName",
                "source": "fileTypeName",
                "type": "TEXT"
            },
            {
                "name": "id",
                "source": "id",
                "type": "TEXT"
            },
            {
                "name": "traceId",
                "source": "traceId",
                "type": "TEXT"
            },
            {
                "name": "uploadId",
                "source": "uploadId",
                "type": "TEXT"
            },
            {
                "name": "uploadName",
                "source": "uploadName",
                "type": "TEXT"
            },
            {
                "name": "uploadTime",
                "source": "uploadTime",
                "type": "TEXT"
            }
        ],
        "dataset_key": "dataset_eaa452c4",
        "key_candidates": [
            "id"
        ],
        "page_name": "启委会管理",
        "parent_record_path": "raw_event.fileVOList[]",
        "partition_field": null,
        "partition_key": null,
        "plugin_id": "dcp-dataset-eaa452c4",
        "record_path": "raw_event.fileVOList[].fileDTOList[]",
        "record_type": "startup_committee:raw_event.fileVOList[].fileDTOList[]",
        "table": "canonical_p009_page_eaa452c4__startup_committee__raw_event_filevolist_items_filedtolist_items"
    },
    {
        "api_name": "weekly_plan",
        "api_path": "/apit/ebuild2-domain-security-risk/v1/weekly/queryWeeklyList",
        "columns": [
            {
                "name": "additionalPlanFlag",
                "source": "additionalPlanFlag",
                "type": "TEXT"
            },
            {
                "name": "anNiu",
                "source": "anNiu",
                "type": "TEXT"
            },
            {
                "name": "auditHierarchy",
                "source": "auditHierarchy",
                "type": "TEXT"
            },
            {
                "name": "biddingSectionCode",
                "source": "biddingSectionCode",
                "type": "TEXT"
            },
            {
                "name": "biddingSectionName",
                "source": "biddingSectionName",
                "type": "TEXT"
            },
            {
                "name": "buildUnitName",
                "source": "buildUnitName",
                "type": "TEXT"
            },
            {
                "name": "createTime",
                "source": "createTime",
                "type": "TEXT"
            },
            {
                "name": "createrId",
                "source": "createrId",
                "type": "TEXT"
            },
            {
                "name": "createrName",
                "source": "createrName",
                "type": "TEXT"
            },
            {
                "name": "currentSignalFlag",
                "source": "currentSignalFlag",
                "type": "INTEGER"
            },
            {
                "name": "deleteFlag",
                "source": "deleteFlag",
                "type": "INTEGER"
            },
            {
                "name": "excelRiskLevel",
                "source": "excelRiskLevel",
                "type": "TEXT"
            },
            {
                "name": "excute",
                "source": "excute",
                "type": "TEXT"
            },
            {
                "name": "excuteFlag",
                "source": "excuteFlag",
                "type": "INTEGER"
            },
            {
                "name": "extra",
                "source": "extra",
                "type": "TEXT"
            },
            {
                "name": "huvFlag",
                "source": "huvFlag",
                "type": "INTEGER"
            },
            {
                "name": "id",
                "source": "id",
                "type": "TEXT"
            },
            {
                "name": "intiRiskLevel",
                "source": "intiRiskLevel",
                "type": "INTEGER"
            },
            {
                "name": "isAudit",
                "source": "isAudit",
                "type": "TEXT"
            },
            {
                "name": "isEdit",
                "source": "isEdit",
                "type": "TEXT"
            },
            {
                "name": "isEditTeam",
                "source": "isEditTeam",
                "type": "TEXT"
            },
            {
                "name": "isRecall",
                "source": "isRecall",
                "type": "TEXT"
            },
            {
                "name": "leaderName",
                "source": "leaderName",
                "type": "TEXT"
            },
            {
                "name": "machs",
                "source": "machs",
                "type": "TEXT"
            },
            {
                "name": "memberCount",
                "source": "memberCount",
                "type": "TEXT"
            },
            {
                "name": "meths",
                "source": "meths",
                "type": "TEXT"
            },
            {
                "name": "nextAuditInfo",
                "source": "nextAuditInfo",
                "type": "TEXT"
            },
            {
                "name": "num",
                "source": "num",
                "type": "TEXT"
            },
            {
                "name": "planStatus",
                "source": "planStatus",
                "type": "TEXT"
            },
            {
                "name": "plannedEndDate",
                "source": "plannedEndDate",
                "type": "TEXT"
            },
            {
                "name": "plannedStartDate",
                "source": "plannedStartDate",
                "type": "TEXT"
            },
            {
                "name": "presentStatus",
                "source": "presentStatus",
                "type": "TEXT"
            },
            {
                "name": "prjCode",
                "source": "prjCode",
                "type": "TEXT"
            },
            {
                "name": "prjName",
                "source": "prjName",
                "type": "TEXT"
            },
            {
                "name": "provinceCode",
                "source": "provinceCode",
                "type": "TEXT"
            },
            {
                "name": "provinceName",
                "source": "provinceName",
                "type": "TEXT"
            },
            {
                "name": "riskLevel",
                "source": "riskLevel",
                "type": "INTEGER"
            },
            {
                "name": "riskStatus",
                "source": "riskStatus",
                "type": "TEXT"
            },
            {
                "name": "singleProjectCode",
                "source": "singleProjectCode",
                "type": "TEXT"
            },
            {
                "name": "singleProjectName",
                "source": "singleProjectName",
                "type": "TEXT"
            },
            {
                "name": "starEndTime",
                "source": "starEndTime",
                "type": "TEXT"
            },
            {
                "name": "subSectionProjectId",
                "source": "subSectionProjectId",
                "type": "TEXT"
            },
            {
                "name": "subSectionProjectName",
                "source": "subSectionProjectName",
                "type": "TEXT"
            },
            {
                "name": "teamId",
                "source": "teamId",
                "type": "TEXT"
            },
            {
                "name": "ticketId",
                "source": "ticketId",
                "type": "TEXT"
            },
            {
                "name": "ticketNo",
                "source": "ticketNo",
                "type": "TEXT"
            },
            {
                "name": "traceId",
                "source": "traceId",
                "type": "TEXT"
            },
            {
                "name": "workProcedure",
                "source": "workProcedure",
                "type": "TEXT"
            },
            {
                "name": "workSiteName",
                "source": "workSiteName",
                "type": "TEXT"
            },
            {
                "name": "workingTeamName",
                "source": "workingTeamName",
                "type": "TEXT"
            }
        ],
        "dataset_key": "dataset_9cea6566",
        "key_candidates": [
            "id",
            "prjCode",
            "singleProjectCode",
            "biddingSectionCode",
            "ticketId",
            "prjCode+singleProjectCode+biddingSectionCode"
        ],
        "page_name": "周计划",
        "parent_record_path": null,
        "partition_field": "prjCode",
        "partition_key": "prjCode",
        "plugin_id": "dcp-dataset-9cea6566",
        "record_path": "raw_event",
        "record_type": "weekly_plan:raw_event",
        "table": "canonical_p010_page_9cea6566__weekly_plan__raw_event"
    },
    {
        "api_name": "countWeeklyList",
        "api_path": "/apit/ebuild2-domain-security-risk/v1/weekly/countWeeklyList",
        "columns": [
            {
                "name": "countWeekAll",
                "source": "countWeekAll",
                "type": "INTEGER"
            },
            {
                "name": "countWeekAlready",
                "source": "countWeekAlready",
                "type": "INTEGER"
            },
            {
                "name": "countWeekCancel",
                "source": "countWeekCancel",
                "type": "INTEGER"
            },
            {
                "name": "countWeekPending",
                "source": "countWeekPending",
                "type": "INTEGER"
            },
            {
                "name": "extra",
                "source": "extra",
                "type": "TEXT"
            },
            {
                "name": "traceId",
                "source": "traceId",
                "type": "TEXT"
            }
        ],
        "dataset_key": "dataset_9cea6566",
        "key_candidates": [
            "source_record_key+record_path"
        ],
        "page_name": "周计划",
        "parent_record_path": null,
        "partition_field": null,
        "partition_key": null,
        "plugin_id": "dcp-dataset-9cea6566",
        "record_path": "raw_event",
        "record_type": "countWeeklyList:raw_event",
        "table": "canonical_p010_page_9cea6566__countweeklylist__raw_event"
    },
    {
        "api_name": "weekly_plan_ledger",
        "api_path": "/apit/ebuild2-domain-security-risk/v1/weekly/queryPage",
        "columns": [
            {
                "name": "additionalPlanFlag",
                "source": "additionalPlanFlag",
                "type": "TEXT"
            },
            {
                "name": "anNiu",
                "source": "anNiu",
                "type": "TEXT"
            },
            {
                "name": "auditHierarchy",
                "source": "auditHierarchy",
                "type": "TEXT"
            },
            {
                "name": "biddingSectionCode",
                "source": "biddingSectionCode",
                "type": "TEXT"
            },
            {
                "name": "biddingSectionName",
                "source": "biddingSectionName",
                "type": "TEXT"
            },
            {
                "name": "buildUnitName",
                "source": "buildUnitName",
                "type": "TEXT"
            },
            {
                "name": "createTime",
                "source": "createTime",
                "type": "TEXT"
            },
            {
                "name": "createrId",
                "source": "createrId",
                "type": "TEXT"
            },
            {
                "name": "createrName",
                "source": "createrName",
                "type": "TEXT"
            },
            {
                "name": "currentSignalFlag",
                "source": "currentSignalFlag",
                "type": "TEXT"
            },
            {
                "name": "deleteFlag",
                "source": "deleteFlag",
                "type": "TEXT"
            },
            {
                "name": "excelRiskLevel",
                "source": "excelRiskLevel",
                "type": "TEXT"
            },
            {
                "name": "excute",
                "source": "excute",
                "type": "TEXT"
            },
            {
                "name": "excuteFlag",
                "source": "excuteFlag",
                "type": "INTEGER"
            },
            {
                "name": "extra",
                "source": "extra",
                "type": "TEXT"
            },
            {
                "name": "huvFlag",
                "source": "huvFlag",
                "type": "INTEGER"
            },
            {
                "name": "id",
                "source": "id",
                "type": "TEXT"
            },
            {
                "name": "intiRiskLevel",
                "source": "intiRiskLevel",
                "type": "TEXT"
            },
            {
                "name": "isAudit",
                "source": "isAudit",
                "type": "TEXT"
            },
            {
                "name": "isEdit",
                "source": "isEdit",
                "type": "TEXT"
            },
            {
                "name": "isEditTeam",
                "source": "isEditTeam",
                "type": "TEXT"
            },
            {
                "name": "isRecall",
                "source": "isRecall",
                "type": "TEXT"
            },
            {
                "name": "leaderName",
                "source": "leaderName",
                "type": "TEXT"
            },
            {
                "name": "machs",
                "source": "machs",
                "type": "TEXT"
            },
            {
                "name": "memberCount",
                "source": "memberCount",
                "type": "TEXT"
            },
            {
                "name": "meths",
                "source": "meths",
                "type": "TEXT"
            },
            {
                "name": "nextAuditInfo",
                "source": "nextAuditInfo",
                "type": "TEXT"
            },
            {
                "name": "num",
                "source": "num",
                "type": "TEXT"
            },
            {
                "name": "planStatus",
                "source": "planStatus",
                "type": "TEXT"
            },
            {
                "name": "plannedEndDate",
                "source": "plannedEndDate",
                "type": "TEXT"
            },
            {
                "name": "plannedStartDate",
                "source": "plannedStartDate",
                "type": "TEXT"
            },
            {
                "name": "presentStatus",
                "source": "presentStatus",
                "type": "TEXT"
            },
            {
                "name": "prjCode",
                "source": "prjCode",
                "type": "TEXT"
            },
            {
                "name": "prjName",
                "source": "prjName",
                "type": "TEXT"
            },
            {
                "name": "provinceCode",
                "source": "provinceCode",
                "type": "TEXT"
            },
            {
                "name": "provinceName",
                "source": "provinceName",
                "type": "TEXT"
            },
            {
                "name": "riskLevel",
                "source": "riskLevel",
                "type": "INTEGER"
            },
            {
                "name": "riskStatus",
                "source": "riskStatus",
                "type": "TEXT"
            },
            {
                "name": "singleProjectCode",
                "source": "singleProjectCode",
                "type": "TEXT"
            },
            {
                "name": "singleProjectName",
                "source": "singleProjectName",
                "type": "TEXT"
            },
            {
                "name": "starEndTime",
                "source": "starEndTime",
                "type": "TEXT"
            },
            {
                "name": "subSectionProjectId",
                "source": "subSectionProjectId",
                "type": "TEXT"
            },
            {
                "name": "subSectionProjectName",
                "source": "subSectionProjectName",
                "type": "TEXT"
            },
            {
                "name": "teamId",
                "source": "teamId",
                "type": "TEXT"
            },
            {
                "name": "ticketId",
                "source": "ticketId",
                "type": "TEXT"
            },
            {
                "name": "ticketNo",
                "source": "ticketNo",
                "type": "TEXT"
            },
            {
                "name": "traceId",
                "source": "traceId",
                "type": "TEXT"
            },
            {
                "name": "workProcedure",
                "source": "workProcedure",
                "type": "TEXT"
            },
            {
                "name": "workSiteName",
                "source": "workSiteName",
                "type": "TEXT"
            },
            {
                "name": "workingTeamName",
                "source": "workingTeamName",
                "type": "TEXT"
            }
        ],
        "dataset_key": "dataset_303fb5ea",
        "key_candidates": [
            "id",
            "prjCode",
            "singleProjectCode",
            "biddingSectionCode",
            "ticketId",
            "prjCode+singleProjectCode+biddingSectionCode"
        ],
        "page_name": "周计划一本账",
        "parent_record_path": null,
        "partition_field": "prjCode",
        "partition_key": "prjCode",
        "plugin_id": "dcp-dataset-303fb5ea",
        "record_path": "raw_event",
        "record_type": "weekly_plan_ledger:raw_event",
        "table": "canonical_p011_page_303fb5ea__weekly_plan_ledger__raw_event"
    },
    {
        "api_name": "project_rework",
        "api_path": "/apit/ebuild2-agg-frame-project/build/returnOrderPageList",
        "columns": [
            {
                "name": "biddingSectionCode",
                "source": "biddingSectionCode",
                "type": "TEXT"
            },
            {
                "name": "chiefSupervisionEngineer",
                "source": "chiefSupervisionEngineer",
                "type": "TEXT"
            },
            {
                "name": "constrPrjDept",
                "source": "constrPrjDept",
                "type": "TEXT"
            },
            {
                "name": "createTime",
                "source": "createTime",
                "type": "INTEGER"
            },
            {
                "name": "createrId",
                "source": "createrId",
                "type": "TEXT"
            },
            {
                "name": "deleteFlag",
                "source": "deleteFlag",
                "type": "TEXT"
            },
            {
                "name": "fileId",
                "source": "fileId",
                "type": "TEXT"
            },
            {
                "name": "id",
                "source": "id",
                "type": "TEXT"
            },
            {
                "name": "issueDate",
                "source": "issueDate",
                "type": "INTEGER"
            },
            {
                "name": "issuerDepId",
                "source": "issuerDepId",
                "type": "TEXT"
            },
            {
                "name": "issuerDepName",
                "source": "issuerDepName",
                "type": "TEXT"
            },
            {
                "name": "pauseNo",
                "source": "pauseNo",
                "type": "TEXT"
            },
            {
                "name": "pausePosition",
                "source": "pausePosition",
                "type": "TEXT"
            },
            {
                "name": "pdfFileId",
                "source": "pdfFileId",
                "type": "TEXT"
            },
            {
                "name": "prjCode",
                "source": "prjCode",
                "type": "TEXT"
            },
            {
                "name": "prjDeptId",
                "source": "prjDeptId",
                "type": "TEXT"
            },
            {
                "name": "prjDeptNo",
                "source": "prjDeptNo",
                "type": "TEXT"
            },
            {
                "name": "projectChargeSeal",
                "source": "projectChargeSeal",
                "type": "TEXT"
            },
            {
                "name": "resumApplicationStatus",
                "source": "resumApplicationStatus",
                "type": "INTEGER"
            },
            {
                "name": "resumeNo",
                "source": "resumeNo",
                "type": "TEXT"
            },
            {
                "name": "resumptionDate",
                "source": "resumptionDate",
                "type": "INTEGER"
            },
            {
                "name": "singleProjectCode",
                "source": "singleProjectCode",
                "type": "TEXT"
            },
            {
                "name": "singleProjectName",
                "source": "singleProjectName",
                "type": "TEXT"
            },
            {
                "name": "suspensionCause",
                "source": "suspensionCause",
                "type": "TEXT"
            },
            {
                "name": "updateTime",
                "source": "updateTime",
                "type": "INTEGER"
            },
            {
                "name": "updaterId",
                "source": "updaterId",
                "type": "TEXT"
            }
        ],
        "dataset_key": "dataset_520e34d1",
        "key_candidates": [
            "id",
            "prjCode",
            "singleProjectCode",
            "biddingSectionCode",
            "prjCode+singleProjectCode+biddingSectionCode"
        ],
        "page_name": "工程复工",
        "parent_record_path": null,
        "partition_field": "prjCode",
        "partition_key": "prjCode",
        "plugin_id": "dcp-dataset-520e34d1",
        "record_path": "raw_event",
        "record_type": "project_rework:raw_event",
        "table": "canonical_p012_page_520e34d1__project_rework__raw_event"
    },
    {
        "api_name": "project_construction_progress",
        "api_path": "/apit/ebuild2-domain-project-stage/v1/prjScheduling/queryPrjList",
        "columns": [
            {
                "name": "actualDuration",
                "source": "actualDuration",
                "type": "TEXT"
            },
            {
                "name": "actualFinDate",
                "source": "actualFinDate",
                "type": "TEXT"
            },
            {
                "name": "actualProgress",
                "source": "actualProgress",
                "type": "REAL"
            },
            {
                "name": "actualStartDate",
                "source": "actualStartDate",
                "type": "TEXT"
            },
            {
                "name": "biddingSectionCode",
                "source": "biddingSectionCode",
                "type": "TEXT"
            },
            {
                "name": "biddingSectionType",
                "source": "biddingSectionType",
                "type": "TEXT"
            },
            {
                "name": "buildUnitCode",
                "source": "buildUnitCode",
                "type": "TEXT"
            },
            {
                "name": "constrTransformerCapacity",
                "source": "constrTransformerCapacity",
                "type": "REAL"
            },
            {
                "name": "constructionLineLength",
                "source": "constructionLineLength",
                "type": "REAL"
            },
            {
                "name": "constructionStatus",
                "source": "constructionStatus",
                "type": "INTEGER"
            },
            {
                "name": "extra",
                "source": "extra",
                "type": "TEXT"
            },
            {
                "name": "id",
                "source": "id",
                "type": "TEXT"
            },
            {
                "name": "messageId",
                "source": "messageId",
                "type": "TEXT"
            },
            {
                "name": "monthlyIncrease",
                "source": "monthlyIncrease",
                "type": "REAL"
            },
            {
                "name": "noUpdateDays",
                "source": "noUpdateDays",
                "type": "INTEGER"
            },
            {
                "name": "orderNum",
                "source": "orderNum",
                "type": "TEXT"
            },
            {
                "name": "planDuration",
                "source": "planDuration",
                "type": "INTEGER"
            },
            {
                "name": "planFinDate",
                "source": "planFinDate",
                "type": "TEXT"
            },
            {
                "name": "planProgress",
                "source": "planProgress",
                "type": "REAL"
            },
            {
                "name": "planStartDate",
                "source": "planStartDate",
                "type": "TEXT"
            },
            {
                "name": "prjActualProgress",
                "source": "prjActualProgress",
                "type": "TEXT"
            },
            {
                "name": "prjCode",
                "source": "prjCode",
                "type": "TEXT"
            },
            {
                "name": "prjName",
                "source": "prjName",
                "type": "TEXT"
            },
            {
                "name": "progressStatus",
                "source": "progressStatus",
                "type": "INTEGER"
            },
            {
                "name": "projectType",
                "source": "projectType",
                "type": "INTEGER"
            },
            {
                "name": "provinceBuildUnitName",
                "source": "provinceBuildUnitName",
                "type": "TEXT"
            },
            {
                "name": "provinceCode",
                "source": "provinceCode",
                "type": "TEXT"
            },
            {
                "name": "rectifyFlag",
                "source": "rectifyFlag",
                "type": "INTEGER"
            },
            {
                "name": "singleActualProgress",
                "source": "singleActualProgress",
                "type": "TEXT"
            },
            {
                "name": "singleProjectCode",
                "source": "singleProjectCode",
                "type": "TEXT"
            },
            {
                "name": "singleProjectDetailsType",
                "source": "singleProjectDetailsType",
                "type": "TEXT"
            },
            {
                "name": "stopFlag",
                "source": "stopFlag",
                "type": "INTEGER"
            },
            {
                "name": "suspensionCause",
                "source": "suspensionCause",
                "type": "TEXT"
            },
            {
                "name": "suspensionCauseType",
                "source": "suspensionCauseType",
                "type": "TEXT"
            },
            {
                "name": "traceId",
                "source": "traceId",
                "type": "TEXT"
            },
            {
                "name": "type",
                "source": "type",
                "type": "INTEGER"
            },
            {
                "name": "updateTime",
                "source": "updateTime",
                "type": "TEXT"
            },
            {
                "name": "warningFlag",
                "source": "warningFlag",
                "type": "INTEGER"
            },
            {
                "name": "weeklyIncrease",
                "source": "weeklyIncrease",
                "type": "REAL"
            },
            {
                "name": "weight",
                "source": "weight",
                "type": "REAL"
            }
        ],
        "dataset_key": "dataset_e40827dc",
        "key_candidates": [
            "id",
            "prjCode",
            "singleProjectCode",
            "biddingSectionCode",
            "prjCode+singleProjectCode+biddingSectionCode"
        ],
        "page_name": "工程建设管理",
        "parent_record_path": null,
        "partition_field": "prjCode",
        "partition_key": "prjCode",
        "plugin_id": "dcp-dataset-e40827dc",
        "record_path": "raw_event",
        "record_type": "project_construction_progress:raw_event",
        "table": "canonical_p013_page_e40827dc__project_construction_progress__raw_event"
    },
    {
        "api_name": "project_construction_progress",
        "api_path": "/apit/ebuild2-domain-project-stage/v1/prjScheduling/queryPrjList",
        "columns": [
            {
                "name": "actualDuration",
                "source": "actualDuration",
                "type": "TEXT"
            },
            {
                "name": "actualFinDate",
                "source": "actualFinDate",
                "type": "TEXT"
            },
            {
                "name": "actualProgress",
                "source": "actualProgress",
                "type": "REAL"
            },
            {
                "name": "actualStartDate",
                "source": "actualStartDate",
                "type": "TEXT"
            },
            {
                "name": "biddingSectionCode",
                "source": "biddingSectionCode",
                "type": "TEXT"
            },
            {
                "name": "biddingSectionType",
                "source": "biddingSectionType",
                "type": "TEXT"
            },
            {
                "name": "buildUnitCode",
                "source": "buildUnitCode",
                "type": "TEXT"
            },
            {
                "name": "constrTransformerCapacity",
                "source": "constrTransformerCapacity",
                "type": "REAL"
            },
            {
                "name": "constructionLineLength",
                "source": "constructionLineLength",
                "type": "REAL"
            },
            {
                "name": "constructionStatus",
                "source": "constructionStatus",
                "type": "TEXT"
            },
            {
                "name": "extra",
                "source": "extra",
                "type": "TEXT"
            },
            {
                "name": "id",
                "source": "id",
                "type": "TEXT"
            },
            {
                "name": "messageId",
                "source": "messageId",
                "type": "TEXT"
            },
            {
                "name": "monthlyIncrease",
                "source": "monthlyIncrease",
                "type": "REAL"
            },
            {
                "name": "noUpdateDays",
                "source": "noUpdateDays",
                "type": "INTEGER"
            },
            {
                "name": "orderNum",
                "source": "orderNum",
                "type": "TEXT"
            },
            {
                "name": "planDuration",
                "source": "planDuration",
                "type": "INTEGER"
            },
            {
                "name": "planFinDate",
                "source": "planFinDate",
                "type": "TEXT"
            },
            {
                "name": "planProgress",
                "source": "planProgress",
                "type": "REAL"
            },
            {
                "name": "planStartDate",
                "source": "planStartDate",
                "type": "TEXT"
            },
            {
                "name": "prjActualProgress",
                "source": "prjActualProgress",
                "type": "TEXT"
            },
            {
                "name": "prjCode",
                "source": "prjCode",
                "type": "TEXT"
            },
            {
                "name": "prjName",
                "source": "prjName",
                "type": "TEXT"
            },
            {
                "name": "progressStatus",
                "source": "progressStatus",
                "type": "TEXT"
            },
            {
                "name": "projectType",
                "source": "projectType",
                "type": "INTEGER"
            },
            {
                "name": "provinceBuildUnitName",
                "source": "provinceBuildUnitName",
                "type": "TEXT"
            },
            {
                "name": "provinceCode",
                "source": "provinceCode",
                "type": "TEXT"
            },
            {
                "name": "rectifyFlag",
                "source": "rectifyFlag",
                "type": "INTEGER"
            },
            {
                "name": "singleActualProgress",
                "source": "singleActualProgress",
                "type": "TEXT"
            },
            {
                "name": "singleProjectCode",
                "source": "singleProjectCode",
                "type": "TEXT"
            },
            {
                "name": "singleProjectDetailsType",
                "source": "singleProjectDetailsType",
                "type": "TEXT"
            },
            {
                "name": "stopFlag",
                "source": "stopFlag",
                "type": "INTEGER"
            },
            {
                "name": "suspensionCause",
                "source": "suspensionCause",
                "type": "TEXT"
            },
            {
                "name": "suspensionCauseType",
                "source": "suspensionCauseType",
                "type": "TEXT"
            },
            {
                "name": "traceId",
                "source": "traceId",
                "type": "TEXT"
            },
            {
                "name": "type",
                "source": "type",
                "type": "INTEGER"
            },
            {
                "name": "updateTime",
                "source": "updateTime",
                "type": "TEXT"
            },
            {
                "name": "warningFlag",
                "source": "warningFlag",
                "type": "TEXT"
            },
            {
                "name": "weeklyIncrease",
                "source": "weeklyIncrease",
                "type": "REAL"
            },
            {
                "name": "weight",
                "source": "weight",
                "type": "REAL"
            }
        ],
        "dataset_key": "dataset_e40827dc",
        "key_candidates": [
            "id",
            "prjCode",
            "singleProjectCode",
            "biddingSectionCode",
            "prjCode+singleProjectCode+biddingSectionCode"
        ],
        "page_name": "工程建设管理",
        "parent_record_path": "raw_event",
        "partition_field": "prjCode",
        "partition_key": "prjCode",
        "plugin_id": "dcp-dataset-e40827dc",
        "record_path": "raw_event.children[]",
        "record_type": "project_construction_progress:raw_event.children[]",
        "table": "canonical_p013_page_e40827dc__project_construction_progress__raw_event_children_items"
    },
    {
        "api_name": "project_construction_progress",
        "api_path": "/apit/ebuild2-domain-project-stage/v1/prjScheduling/queryPrjList",
        "columns": [
            {
                "name": "actualDuration",
                "source": "actualDuration",
                "type": "TEXT"
            },
            {
                "name": "actualFinDate",
                "source": "actualFinDate",
                "type": "TEXT"
            },
            {
                "name": "actualProgress",
                "source": "actualProgress",
                "type": "REAL"
            },
            {
                "name": "actualStartDate",
                "source": "actualStartDate",
                "type": "TEXT"
            },
            {
                "name": "biddingSectionCode",
                "source": "biddingSectionCode",
                "type": "TEXT"
            },
            {
                "name": "biddingSectionType",
                "source": "biddingSectionType",
                "type": "TEXT"
            },
            {
                "name": "buildUnitCode",
                "source": "buildUnitCode",
                "type": "TEXT"
            },
            {
                "name": "children",
                "source": "children",
                "type": "TEXT"
            },
            {
                "name": "constrTransformerCapacity",
                "source": "constrTransformerCapacity",
                "type": "TEXT"
            },
            {
                "name": "constructionLineLength",
                "source": "constructionLineLength",
                "type": "REAL"
            },
            {
                "name": "constructionStatus",
                "source": "constructionStatus",
                "type": "TEXT"
            },
            {
                "name": "extra",
                "source": "extra",
                "type": "TEXT"
            },
            {
                "name": "id",
                "source": "id",
                "type": "TEXT"
            },
            {
                "name": "messageId",
                "source": "messageId",
                "type": "TEXT"
            },
            {
                "name": "monthlyIncrease",
                "source": "monthlyIncrease",
                "type": "REAL"
            },
            {
                "name": "noUpdateDays",
                "source": "noUpdateDays",
                "type": "INTEGER"
            },
            {
                "name": "orderNum",
                "source": "orderNum",
                "type": "TEXT"
            },
            {
                "name": "planDuration",
                "source": "planDuration",
                "type": "INTEGER"
            },
            {
                "name": "planFinDate",
                "source": "planFinDate",
                "type": "TEXT"
            },
            {
                "name": "planProgress",
                "source": "planProgress",
                "type": "REAL"
            },
            {
                "name": "planStartDate",
                "source": "planStartDate",
                "type": "TEXT"
            },
            {
                "name": "prjActualProgress",
                "source": "prjActualProgress",
                "type": "TEXT"
            },
            {
                "name": "prjCode",
                "source": "prjCode",
                "type": "TEXT"
            },
            {
                "name": "prjName",
                "source": "prjName",
                "type": "TEXT"
            },
            {
                "name": "progressStatus",
                "source": "progressStatus",
                "type": "TEXT"
            },
            {
                "name": "projectType",
                "source": "projectType",
                "type": "TEXT"
            },
            {
                "name": "provinceBuildUnitName",
                "source": "provinceBuildUnitName",
                "type": "TEXT"
            },
            {
                "name": "provinceCode",
                "source": "provinceCode",
                "type": "TEXT"
            },
            {
                "name": "rectifyFlag",
                "source": "rectifyFlag",
                "type": "INTEGER"
            },
            {
                "name": "singleActualProgress",
                "source": "singleActualProgress",
                "type": "TEXT"
            },
            {
                "name": "singleProjectCode",
                "source": "singleProjectCode",
                "type": "TEXT"
            },
            {
                "name": "singleProjectDetailsType",
                "source": "singleProjectDetailsType",
                "type": "TEXT"
            },
            {
                "name": "stopFlag",
                "source": "stopFlag",
                "type": "INTEGER"
            },
            {
                "name": "suspensionCause",
                "source": "suspensionCause",
                "type": "TEXT"
            },
            {
                "name": "suspensionCauseType",
                "source": "suspensionCauseType",
                "type": "TEXT"
            },
            {
                "name": "traceId",
                "source": "traceId",
                "type": "TEXT"
            },
            {
                "name": "type",
                "source": "type",
                "type": "INTEGER"
            },
            {
                "name": "updateTime",
                "source": "updateTime",
                "type": "TEXT"
            },
            {
                "name": "warningFlag",
                "source": "warningFlag",
                "type": "TEXT"
            },
            {
                "name": "weeklyIncrease",
                "source": "weeklyIncrease",
                "type": "REAL"
            },
            {
                "name": "weight",
                "source": "weight",
                "type": "REAL"
            }
        ],
        "dataset_key": "dataset_e40827dc",
        "key_candidates": [
            "id",
            "prjCode",
            "singleProjectCode",
            "biddingSectionCode",
            "prjCode+singleProjectCode+biddingSectionCode"
        ],
        "page_name": "工程建设管理",
        "parent_record_path": "raw_event.children[]",
        "partition_field": "prjCode",
        "partition_key": "prjCode",
        "plugin_id": "dcp-dataset-e40827dc",
        "record_path": "raw_event.children[].children[]",
        "record_type": "project_construction_progress:raw_event.children[].children[]",
        "table": "canonical_p013_page_e40827dc__project_construction_progress__raw_event_children_items_children_items"
    },
    {
        "api_name": "project_management_outline",
        "api_path": "/apit/ebuild2-domain-project-stage/v1/conOutline/queryOutlinePage",
        "columns": [
            {
                "name": "extra",
                "source": "extra",
                "type": "TEXT"
            },
            {
                "name": "fileId",
                "source": "fileId",
                "type": "TEXT"
            },
            {
                "name": "fileName",
                "source": "fileName",
                "type": "TEXT"
            },
            {
                "name": "id",
                "source": "id",
                "type": "TEXT"
            },
            {
                "name": "lastUploadDate",
                "source": "lastUploadDate",
                "type": "TEXT"
            },
            {
                "name": "revisionFileName",
                "source": "revisionFileName",
                "type": "TEXT"
            },
            {
                "name": "subUnitName",
                "source": "subUnitName",
                "type": "TEXT"
            },
            {
                "name": "traceId",
                "source": "traceId",
                "type": "TEXT"
            }
        ],
        "dataset_key": "dataset_09285810",
        "key_candidates": [
            "id"
        ],
        "page_name": "工程建设管理纲要",
        "parent_record_path": null,
        "partition_field": null,
        "partition_key": null,
        "plugin_id": "dcp-dataset-09285810",
        "record_path": "raw_event",
        "record_type": "project_management_outline:raw_event",
        "table": "canonical_p014_page_09285810__project_management_outline__raw_event"
    },
    {
        "api_name": "project_management_outline",
        "api_path": "/apit/ebuild2-domain-project-stage/v1/conOutline/queryOutlinePage",
        "columns": [
            {
                "name": "relaFlag",
                "source": "relaFlag",
                "type": "TEXT"
            },
            {
                "name": "singleProjectCode",
                "source": "singleProjectCode",
                "type": "TEXT"
            },
            {
                "name": "singleProjectName",
                "source": "singleProjectName",
                "type": "TEXT"
            }
        ],
        "dataset_key": "dataset_09285810",
        "key_candidates": [
            "singleProjectCode"
        ],
        "page_name": "工程建设管理纲要",
        "parent_record_path": "raw_event",
        "partition_field": "singleProjectCode",
        "partition_key": "singleProjectCode",
        "plugin_id": "dcp-dataset-09285810",
        "record_path": "raw_event.sinPrjList[]",
        "record_type": "project_management_outline:raw_event.sinPrjList[]",
        "table": "canonical_p014_page_09285810__project_management_outline__raw_event_sinprjlist_items"
    },
    {
        "api_name": "commencement_order_create_form",
        "api_path": "/apit/ebuild2-domain-project-stage/v1/commenOrder/createDS",
        "columns": [
            {
                "name": "actualCommencementDate",
                "source": "actualCommencementDate",
                "type": "TEXT"
            },
            {
                "name": "appCommenDate",
                "source": "appCommenDate",
                "type": "TEXT"
            },
            {
                "name": "applicationNo",
                "source": "applicationNo",
                "type": "TEXT"
            },
            {
                "name": "bidSectNameOnBidSect",
                "source": "bidSectNameOnBidSect",
                "type": "TEXT"
            },
            {
                "name": "bidSectType",
                "source": "bidSectType",
                "type": "INTEGER"
            },
            {
                "name": "bidTime",
                "source": "bidTime",
                "type": "INTEGER"
            },
            {
                "name": "biddingSectionCode",
                "source": "biddingSectionCode",
                "type": "TEXT"
            },
            {
                "name": "biddingSectionName",
                "source": "biddingSectionName",
                "type": "TEXT"
            },
            {
                "name": "commInfoFlag",
                "source": "commInfoFlag",
                "type": "INTEGER"
            },
            {
                "name": "commenAppInfoFileId",
                "source": "commenAppInfoFileId",
                "type": "TEXT"
            },
            {
                "name": "constrDeptName",
                "source": "constrDeptName",
                "type": "TEXT"
            },
            {
                "name": "constrNature",
                "source": "constrNature",
                "type": "INTEGER"
            },
            {
                "name": "constrNatureText",
                "source": "constrNatureText",
                "type": "TEXT"
            },
            {
                "name": "constrPrjDeptNo",
                "source": "constrPrjDeptNo",
                "type": "TEXT"
            },
            {
                "name": "constrTransCapacity",
                "source": "constrTransCapacity",
                "type": "REAL"
            },
            {
                "name": "fileId",
                "source": "fileId",
                "type": "TEXT"
            },
            {
                "name": "id",
                "source": "id",
                "type": "TEXT"
            },
            {
                "name": "initialDesignApprovalDate",
                "source": "initialDesignApprovalDate",
                "type": "INTEGER"
            },
            {
                "name": "instanceId",
                "source": "instanceId",
                "type": "TEXT"
            },
            {
                "name": "issueDate",
                "source": "issueDate",
                "type": "TEXT"
            },
            {
                "name": "prjCode",
                "source": "prjCode",
                "type": "TEXT"
            },
            {
                "name": "prjManageMode",
                "source": "prjManageMode",
                "type": "INTEGER"
            },
            {
                "name": "prjName",
                "source": "prjName",
                "type": "TEXT"
            },
            {
                "name": "projectType",
                "source": "projectType",
                "type": "INTEGER"
            },
            {
                "name": "remark",
                "source": "remark",
                "type": "TEXT"
            },
            {
                "name": "signTime",
                "source": "signTime",
                "type": "INTEGER"
            },
            {
                "name": "singleActualCommissioningDate",
                "source": "singleActualCommissioningDate",
                "type": "TEXT"
            },
            {
                "name": "singleProjectCode",
                "source": "singleProjectCode",
                "type": "TEXT"
            },
            {
                "name": "singleProjectName",
                "source": "singleProjectName",
                "type": "TEXT"
            },
            {
                "name": "singleProjectType",
                "source": "singleProjectType",
                "type": "INTEGER"
            },
            {
                "name": "singleProjectTypeText",
                "source": "singleProjectTypeText",
                "type": "TEXT"
            },
            {
                "name": "status",
                "source": "status",
                "type": "INTEGER"
            },
            {
                "name": "supervisorFlag",
                "source": "supervisorFlag",
                "type": "INTEGER"
            },
            {
                "name": "volLevel",
                "source": "volLevel",
                "type": "TEXT"
            }
        ],
        "dataset_key": "dataset_22049cc1",
        "key_candidates": [
            "id",
            "prjCode",
            "singleProjectCode",
            "biddingSectionCode",
            "prjCode+singleProjectCode+biddingSectionCode"
        ],
        "page_name": "工程开工令",
        "parent_record_path": null,
        "partition_field": "prjCode",
        "partition_key": "prjCode",
        "plugin_id": "dcp-dataset-22049cc1",
        "record_path": "raw_event",
        "record_type": "commencement_order_create_form:raw_event",
        "table": "canonical_p015_page_22049cc1__commencement_order_create_form__raw_event"
    },
    {
        "api_name": "commencement_order_create_form",
        "api_path": "/apit/ebuild2-domain-project-stage/v1/commenOrder/createDS",
        "columns": [
            {
                "name": "applicationCommenDate",
                "source": "applicationCommenDate",
                "type": "TEXT"
            },
            {
                "name": "biddingSectionCode",
                "source": "biddingSectionCode",
                "type": "TEXT"
            },
            {
                "name": "fileId",
                "source": "fileId",
                "type": "TEXT"
            },
            {
                "name": "fileName",
                "source": "fileName",
                "type": "TEXT"
            },
            {
                "name": "id",
                "source": "id",
                "type": "TEXT"
            },
            {
                "name": "instanceId",
                "source": "instanceId",
                "type": "TEXT"
            }
        ],
        "dataset_key": "dataset_22049cc1",
        "key_candidates": [
            "id",
            "biddingSectionCode"
        ],
        "page_name": "工程开工令",
        "parent_record_path": "raw_event",
        "partition_field": "biddingSectionCode",
        "partition_key": "biddingSectionCode",
        "plugin_id": "dcp-dataset-22049cc1",
        "record_path": "raw_event.commenInfoFileList[]",
        "record_type": "commencement_order_create_form:raw_event.commenInfoFileList[]",
        "table": "canonical_p015_page_22049cc1__commencement_order_create_form__raw_event_commeninfofilelist_items"
    },
    {
        "api_name": "project_summary",
        "api_path": "/apit/ebuild2-domain-project-stage/v1/engineerSummary/getPageResult",
        "columns": [
            {
                "name": "deptId",
                "source": "deptId",
                "type": "TEXT"
            },
            {
                "name": "deptName",
                "source": "deptName",
                "type": "TEXT"
            },
            {
                "name": "establishmentDate",
                "source": "establishmentDate",
                "type": "TEXT"
            },
            {
                "name": "fileId",
                "source": "fileId",
                "type": "TEXT"
            },
            {
                "name": "fileName",
                "source": "fileName",
                "type": "TEXT"
            },
            {
                "name": "summaryType",
                "source": "summaryType",
                "type": "TEXT"
            },
            {
                "name": "updateTime",
                "source": "updateTime",
                "type": "TEXT"
            }
        ],
        "dataset_key": "dataset_8c420f1b",
        "key_candidates": [
            "source_record_key+record_path"
        ],
        "page_name": "工程总结汇总",
        "parent_record_path": null,
        "partition_field": null,
        "partition_key": null,
        "plugin_id": "dcp-dataset-8c420f1b",
        "record_path": "raw_event",
        "record_type": "project_summary:raw_event",
        "table": "canonical_p016_page_8c420f1b__project_summary__raw_event"
    },
    {
        "api_name": "getSingleProjectInfo",
        "api_path": "/apit/ebuild2-domain-project-stage/v1/engineerSummary/getSingleProjectInfo",
        "columns": [
            {
                "name": "actualCommencementDate",
                "source": "actualCommencementDate",
                "type": "TEXT"
            },
            {
                "name": "actualCommissioningDate",
                "source": "actualCommissioningDate",
                "type": "TEXT"
            },
            {
                "name": "bidSectInfoDTOList",
                "source": "bidSectInfoDTOList",
                "type": "TEXT"
            },
            {
                "name": "fileId",
                "source": "fileId",
                "type": "TEXT"
            },
            {
                "name": "fileName",
                "source": "fileName",
                "type": "TEXT"
            },
            {
                "name": "fileSize",
                "source": "fileSize",
                "type": "TEXT"
            },
            {
                "name": "plannedCommencementDate",
                "source": "plannedCommencementDate",
                "type": "TEXT"
            },
            {
                "name": "plannedCommissioningDate",
                "source": "plannedCommissioningDate",
                "type": "TEXT"
            },
            {
                "name": "singleProjectCode",
                "source": "singleProjectCode",
                "type": "TEXT"
            },
            {
                "name": "singleProjectName",
                "source": "singleProjectName",
                "type": "TEXT"
            },
            {
                "name": "status",
                "source": "status",
                "type": "TEXT"
            }
        ],
        "dataset_key": "dataset_8c420f1b",
        "key_candidates": [
            "singleProjectCode"
        ],
        "page_name": "工程总结汇总",
        "parent_record_path": null,
        "partition_field": "singleProjectCode",
        "partition_key": "singleProjectCode",
        "plugin_id": "dcp-dataset-8c420f1b",
        "record_path": "raw_event",
        "record_type": "getSingleProjectInfo:raw_event",
        "table": "canonical_p016_page_8c420f1b__getsingleprojectinfo__raw_event"
    },
    {
        "api_name": "project_pause",
        "api_path": "/apit/ebuild2-agg-frame-project/build/pageQueryBuildPauseOrder",
        "columns": [
            {
                "name": "appliDate",
                "source": "appliDate",
                "type": "INTEGER"
            },
            {
                "name": "applicant",
                "source": "applicant",
                "type": "TEXT"
            },
            {
                "name": "askFor",
                "source": "askFor",
                "type": "TEXT"
            },
            {
                "name": "biddingSectionCode",
                "source": "biddingSectionCode",
                "type": "TEXT"
            },
            {
                "name": "businessId",
                "source": "businessId",
                "type": "TEXT"
            },
            {
                "name": "chiefSupervisionEngineer",
                "source": "chiefSupervisionEngineer",
                "type": "TEXT"
            },
            {
                "name": "constrPrjDept",
                "source": "constrPrjDept",
                "type": "TEXT"
            },
            {
                "name": "createTime",
                "source": "createTime",
                "type": "INTEGER"
            },
            {
                "name": "createrId",
                "source": "createrId",
                "type": "TEXT"
            },
            {
                "name": "currentStatus",
                "source": "currentStatus",
                "type": "INTEGER"
            },
            {
                "name": "deleteFlag",
                "source": "deleteFlag",
                "type": "INTEGER"
            },
            {
                "name": "executType",
                "source": "executType",
                "type": "INTEGER"
            },
            {
                "name": "fileId",
                "source": "fileId",
                "type": "TEXT"
            },
            {
                "name": "id",
                "source": "id",
                "type": "TEXT"
            },
            {
                "name": "isCanRecall",
                "source": "isCanRecall",
                "type": "INTEGER"
            },
            {
                "name": "issueDate",
                "source": "issueDate",
                "type": "INTEGER"
            },
            {
                "name": "issuer",
                "source": "issuer",
                "type": "TEXT"
            },
            {
                "name": "issuerDepId",
                "source": "issuerDepId",
                "type": "TEXT"
            },
            {
                "name": "issuerDepName",
                "source": "issuerDepName",
                "type": "TEXT"
            },
            {
                "name": "nodeId",
                "source": "nodeId",
                "type": "TEXT"
            },
            {
                "name": "pauseNo",
                "source": "pauseNo",
                "type": "TEXT"
            },
            {
                "name": "pausePosition",
                "source": "pausePosition",
                "type": "TEXT"
            },
            {
                "name": "pdfFileId",
                "source": "pdfFileId",
                "type": "TEXT"
            },
            {
                "name": "prjCode",
                "source": "prjCode",
                "type": "TEXT"
            },
            {
                "name": "prjDeptId",
                "source": "prjDeptId",
                "type": "TEXT"
            },
            {
                "name": "prjName",
                "source": "prjName",
                "type": "TEXT"
            },
            {
                "name": "reType",
                "source": "reType",
                "type": "INTEGER"
            },
            {
                "name": "resumApplicationStatus",
                "source": "resumApplicationStatus",
                "type": "INTEGER"
            },
            {
                "name": "singleProjectCode",
                "source": "singleProjectCode",
                "type": "TEXT"
            },
            {
                "name": "singleProjectName",
                "source": "singleProjectName",
                "type": "TEXT"
            },
            {
                "name": "supvPrjDeptSeal",
                "source": "supvPrjDeptSeal",
                "type": "TEXT"
            },
            {
                "name": "suspensionCause",
                "source": "suspensionCause",
                "type": "TEXT"
            },
            {
                "name": "suspensionDate",
                "source": "suspensionDate",
                "type": "INTEGER"
            },
            {
                "name": "updateTime",
                "source": "updateTime",
                "type": "INTEGER"
            },
            {
                "name": "updaterId",
                "source": "updaterId",
                "type": "TEXT"
            }
        ],
        "dataset_key": "dataset_989b3acc",
        "key_candidates": [
            "id",
            "prjCode",
            "singleProjectCode",
            "biddingSectionCode",
            "prjCode+singleProjectCode+biddingSectionCode"
        ],
        "page_name": "工程暂停令",
        "parent_record_path": null,
        "partition_field": "prjCode",
        "partition_key": "prjCode",
        "plugin_id": "dcp-dataset-989b3acc",
        "record_path": "raw_event",
        "record_type": "project_pause:raw_event",
        "table": "canonical_p017_page_989b3acc__project_pause__raw_event"
    },
    {
        "api_name": "yearly_blackout_plan",
        "api_path": "/apit/ebuild2-domain-plan-foundation/v1/yearBlackoutPlanLookAndSend/getYearBlackoutPlan",
        "columns": [
            {
                "name": "auditStatus",
                "source": "auditStatus",
                "type": "TEXT"
            },
            {
                "name": "auditUserName",
                "source": "auditUserName",
                "type": "TEXT"
            },
            {
                "name": "blackoutCode",
                "source": "blackoutCode",
                "type": "TEXT"
            },
            {
                "name": "blackoutEndDate",
                "source": "blackoutEndDate",
                "type": "TEXT"
            },
            {
                "name": "blackoutId",
                "source": "blackoutId",
                "type": "TEXT"
            },
            {
                "name": "blackoutIds",
                "source": "blackoutIds",
                "type": "TEXT"
            },
            {
                "name": "blackoutName",
                "source": "blackoutName",
                "type": "TEXT"
            },
            {
                "name": "blackoutStartDate",
                "source": "blackoutStartDate",
                "type": "TEXT"
            },
            {
                "name": "compilerUserName",
                "source": "compilerUserName",
                "type": "TEXT"
            },
            {
                "name": "equipmentName",
                "source": "equipmentName",
                "type": "TEXT"
            },
            {
                "name": "id",
                "source": "id",
                "type": "TEXT"
            },
            {
                "name": "jobContentFive",
                "source": "jobContentFive",
                "type": "TEXT"
            },
            {
                "name": "jobContentFour",
                "source": "jobContentFour",
                "type": "TEXT"
            },
            {
                "name": "jobContentOne",
                "source": "jobContentOne",
                "type": "TEXT"
            },
            {
                "name": "jobContentSeven",
                "source": "jobContentSeven",
                "type": "TEXT"
            },
            {
                "name": "jobContentSix",
                "source": "jobContentSix",
                "type": "TEXT"
            },
            {
                "name": "jobContentThree",
                "source": "jobContentThree",
                "type": "TEXT"
            },
            {
                "name": "jobContentTwo",
                "source": "jobContentTwo",
                "type": "TEXT"
            },
            {
                "name": "level",
                "source": "level",
                "type": "TEXT"
            },
            {
                "name": "minBlackoutStartDate",
                "source": "minBlackoutStartDate",
                "type": "TEXT"
            },
            {
                "name": "notReportedProvinceName",
                "source": "notReportedProvinceName",
                "type": "TEXT"
            },
            {
                "name": "notReportedProvinceNum",
                "source": "notReportedProvinceNum",
                "type": "TEXT"
            },
            {
                "name": "outageDuration",
                "source": "outageDuration",
                "type": "INTEGER"
            },
            {
                "name": "overhaulId",
                "source": "overhaulId",
                "type": "TEXT"
            },
            {
                "name": "planMonth",
                "source": "planMonth",
                "type": "TEXT"
            },
            {
                "name": "planSingleProjectNum",
                "source": "planSingleProjectNum",
                "type": "TEXT"
            },
            {
                "name": "planYear",
                "source": "planYear",
                "type": "TEXT"
            },
            {
                "name": "prjCode",
                "source": "prjCode",
                "type": "TEXT"
            },
            {
                "name": "prjName",
                "source": "prjName",
                "type": "TEXT"
            },
            {
                "name": "provinceCode",
                "source": "provinceCode",
                "type": "TEXT"
            },
            {
                "name": "provinceName",
                "source": "provinceName",
                "type": "TEXT"
            },
            {
                "name": "reportTime",
                "source": "reportTime",
                "type": "TEXT"
            },
            {
                "name": "reportedProvinceName",
                "source": "reportedProvinceName",
                "type": "TEXT"
            },
            {
                "name": "reportedProvinceNum",
                "source": "reportedProvinceNum",
                "type": "TEXT"
            },
            {
                "name": "returnedOpinions",
                "source": "returnedOpinions",
                "type": "TEXT"
            },
            {
                "name": "reviewTime",
                "source": "reviewTime",
                "type": "TEXT"
            },
            {
                "name": "singleProjectCode",
                "source": "singleProjectCode",
                "type": "TEXT"
            },
            {
                "name": "singleProjectName",
                "source": "singleProjectName",
                "type": "TEXT"
            },
            {
                "name": "submitTime",
                "source": "submitTime",
                "type": "TEXT"
            },
            {
                "name": "userName",
                "source": "userName",
                "type": "TEXT"
            },
            {
                "name": "voltageLevel",
                "source": "voltageLevel",
                "type": "TEXT"
            }
        ],
        "dataset_key": "dataset_23a6ebab",
        "key_candidates": [
            "id",
            "prjCode",
            "singleProjectCode",
            "prjCode+singleProjectCode"
        ],
        "page_name": "年度停电计划查看",
        "parent_record_path": null,
        "partition_field": "prjCode",
        "partition_key": "prjCode",
        "plugin_id": "dcp-dataset-23a6ebab",
        "record_path": "raw_event",
        "record_type": "yearly_blackout_plan:raw_event",
        "table": "canonical_p018_page_23a6ebab__yearly_blackout_plan__raw_event"
    },
    {
        "api_name": "yearly_blackout_plan",
        "api_path": "/apit/ebuild2-domain-plan-foundation/v1/yearBlackoutPlanLookAndSend/getYearBlackoutPlan",
        "columns": [
            {
                "name": "auditStatus",
                "source": "auditStatus",
                "type": "TEXT"
            },
            {
                "name": "auditUserName",
                "source": "auditUserName",
                "type": "TEXT"
            },
            {
                "name": "blackoutCode",
                "source": "blackoutCode",
                "type": "TEXT"
            },
            {
                "name": "blackoutEndDate",
                "source": "blackoutEndDate",
                "type": "TEXT"
            },
            {
                "name": "blackoutId",
                "source": "blackoutId",
                "type": "TEXT"
            },
            {
                "name": "blackoutIds",
                "source": "blackoutIds",
                "type": "TEXT"
            },
            {
                "name": "blackoutName",
                "source": "blackoutName",
                "type": "TEXT"
            },
            {
                "name": "blackoutStartDate",
                "source": "blackoutStartDate",
                "type": "TEXT"
            },
            {
                "name": "compilerUserName",
                "source": "compilerUserName",
                "type": "TEXT"
            },
            {
                "name": "equipmentName",
                "source": "equipmentName",
                "type": "TEXT"
            },
            {
                "name": "id",
                "source": "id",
                "type": "TEXT"
            },
            {
                "name": "jobContentFive",
                "source": "jobContentFive",
                "type": "TEXT"
            },
            {
                "name": "jobContentFour",
                "source": "jobContentFour",
                "type": "TEXT"
            },
            {
                "name": "jobContentOne",
                "source": "jobContentOne",
                "type": "TEXT"
            },
            {
                "name": "jobContentSeven",
                "source": "jobContentSeven",
                "type": "TEXT"
            },
            {
                "name": "jobContentSix",
                "source": "jobContentSix",
                "type": "TEXT"
            },
            {
                "name": "jobContentThree",
                "source": "jobContentThree",
                "type": "TEXT"
            },
            {
                "name": "jobContentTwo",
                "source": "jobContentTwo",
                "type": "TEXT"
            },
            {
                "name": "level",
                "source": "level",
                "type": "TEXT"
            },
            {
                "name": "minBlackoutStartDate",
                "source": "minBlackoutStartDate",
                "type": "TEXT"
            },
            {
                "name": "notReportedProvinceName",
                "source": "notReportedProvinceName",
                "type": "TEXT"
            },
            {
                "name": "notReportedProvinceNum",
                "source": "notReportedProvinceNum",
                "type": "TEXT"
            },
            {
                "name": "outageDuration",
                "source": "outageDuration",
                "type": "INTEGER"
            },
            {
                "name": "overhaulId",
                "source": "overhaulId",
                "type": "TEXT"
            },
            {
                "name": "planMonth",
                "source": "planMonth",
                "type": "TEXT"
            },
            {
                "name": "planSingleProjectNum",
                "source": "planSingleProjectNum",
                "type": "TEXT"
            },
            {
                "name": "planYear",
                "source": "planYear",
                "type": "TEXT"
            },
            {
                "name": "prjCode",
                "source": "prjCode",
                "type": "TEXT"
            },
            {
                "name": "prjName",
                "source": "prjName",
                "type": "TEXT"
            },
            {
                "name": "provinceCode",
                "source": "provinceCode",
                "type": "TEXT"
            },
            {
                "name": "provinceName",
                "source": "provinceName",
                "type": "TEXT"
            },
            {
                "name": "reportTime",
                "source": "reportTime",
                "type": "TEXT"
            },
            {
                "name": "reportedProvinceName",
                "source": "reportedProvinceName",
                "type": "TEXT"
            },
            {
                "name": "reportedProvinceNum",
                "source": "reportedProvinceNum",
                "type": "TEXT"
            },
            {
                "name": "returnedOpinions",
                "source": "returnedOpinions",
                "type": "TEXT"
            },
            {
                "name": "reviewTime",
                "source": "reviewTime",
                "type": "TEXT"
            },
            {
                "name": "singleProjectCode",
                "source": "singleProjectCode",
                "type": "TEXT"
            },
            {
                "name": "singleProjectName",
                "source": "singleProjectName",
                "type": "TEXT"
            },
            {
                "name": "submitTime",
                "source": "submitTime",
                "type": "TEXT"
            },
            {
                "name": "userName",
                "source": "userName",
                "type": "TEXT"
            },
            {
                "name": "voltageLevel",
                "source": "voltageLevel",
                "type": "TEXT"
            }
        ],
        "dataset_key": "dataset_3a3f9598",
        "key_candidates": [
            "id",
            "prjCode",
            "singleProjectCode",
            "prjCode+singleProjectCode"
        ],
        "page_name": "年度停电计划编制",
        "parent_record_path": null,
        "partition_field": "prjCode",
        "partition_key": "prjCode",
        "plugin_id": "dcp-dataset-3a3f9598",
        "record_path": "raw_event",
        "record_type": "yearly_blackout_plan:raw_event",
        "table": "canonical_p019_page_3a3f9598__yearly_blackout_plan__raw_event"
    },
    {
        "api_name": "yearly_progress_analysis",
        "api_path": "/apit/ebuild2-domain-plan-progress/v1/provincePlanView/queryBeforeAfterDetail",
        "columns": [
            {
                "name": "adjustCause",
                "source": "adjustCause",
                "type": "TEXT"
            },
            {
                "name": "adjustType",
                "source": "adjustType",
                "type": "TEXT"
            },
            {
                "name": "apprFileNo",
                "source": "apprFileNo",
                "type": "TEXT"
            },
            {
                "name": "azksTime",
                "source": "azksTime",
                "type": "TEXT"
            },
            {
                "name": "buildProcessId",
                "source": "buildProcessId",
                "type": "TEXT"
            },
            {
                "name": "buildUnitCode",
                "source": "buildUnitCode",
                "type": "TEXT"
            },
            {
                "name": "buildUnitName",
                "source": "buildUnitName",
                "type": "TEXT"
            },
            {
                "name": "cbStart",
                "source": "cbStart",
                "type": "INTEGER"
            },
            {
                "name": "cbStartName",
                "source": "cbStartName",
                "type": "TEXT"
            },
            {
                "name": "cbsjpsTime",
                "source": "cbsjpsTime",
                "type": "TEXT"
            },
            {
                "name": "cbsjpsyjxdTime",
                "source": "cbsjpsyjxdTime",
                "type": "TEXT"
            },
            {
                "name": "constrAddress",
                "source": "constrAddress",
                "type": "TEXT"
            },
            {
                "name": "constrNature",
                "source": "constrNature",
                "type": "INTEGER"
            },
            {
                "name": "constrNatureName",
                "source": "constrNatureName",
                "type": "TEXT"
            },
            {
                "name": "constrTransformerCapacity",
                "source": "constrTransformerCapacity",
                "type": "REAL"
            },
            {
                "name": "constrTransformerCapacityList",
                "source": "constrTransformerCapacityList",
                "type": "TEXT"
            },
            {
                "name": "constructionCategory",
                "source": "constructionCategory",
                "type": "INTEGER"
            },
            {
                "name": "constructionCategoryName",
                "source": "constructionCategoryName",
                "type": "TEXT"
            },
            {
                "name": "constructionLineLength",
                "source": "constructionLineLength",
                "type": "REAL"
            },
            {
                "name": "constructionLineLengthList",
                "source": "constructionLineLengthList",
                "type": "TEXT"
            },
            {
                "name": "createTime",
                "source": "createTime",
                "type": "TEXT"
            },
            {
                "name": "createType",
                "source": "createType",
                "type": "INTEGER"
            },
            {
                "name": "createrId",
                "source": "createrId",
                "type": "TEXT"
            },
            {
                "name": "cspfTime",
                "source": "cspfTime",
                "type": "TEXT"
            },
            {
                "name": "currentBudget",
                "source": "currentBudget",
                "type": "REAL"
            },
            {
                "name": "currentInvestment",
                "source": "currentInvestment",
                "type": "REAL"
            },
            {
                "name": "dazlyjTime",
                "source": "dazlyjTime",
                "type": "TEXT"
            },
            {
                "name": "deleteFlag",
                "source": "deleteFlag",
                "type": "INTEGER"
            },
            {
                "name": "durationMonths",
                "source": "durationMonths",
                "type": "INTEGER"
            },
            {
                "name": "extra",
                "source": "extra",
                "type": "TEXT"
            },
            {
                "name": "feaDinvest",
                "source": "feaDinvest",
                "type": "TEXT"
            },
            {
                "name": "feaLineLength",
                "source": "feaLineLength",
                "type": "TEXT"
            },
            {
                "name": "feaSinvest",
                "source": "feaSinvest",
                "type": "TEXT"
            },
            {
                "name": "feasTransCapacity",
                "source": "feasTransCapacity",
                "type": "TEXT"
            },
            {
                "name": "hbysTime",
                "source": "hbysTime",
                "type": "TEXT"
            },
            {
                "name": "hppfTime",
                "source": "hppfTime",
                "type": "TEXT"
            },
            {
                "name": "hqProcessId",
                "source": "hqProcessId",
                "type": "TEXT"
            },
            {
                "name": "hzTime",
                "source": "hzTime",
                "type": "TEXT"
            },
            {
                "name": "id",
                "source": "id",
                "type": "TEXT"
            },
            {
                "name": "imageProgress",
                "source": "imageProgress",
                "type": "TEXT"
            },
            {
                "name": "jgjsTime",
                "source": "jgjsTime",
                "type": "TEXT"
            },
            {
                "name": "jhjgTime",
                "source": "jhjgTime",
                "type": "TEXT"
            },
            {
                "name": "jhkgTime",
                "source": "jhkgTime",
                "type": "TEXT"
            },
            {
                "name": "jhkgTimeList",
                "source": "jhkgTimeList",
                "type": "TEXT"
            },
            {
                "name": "jhtcTime",
                "source": "jhtcTime",
                "type": "TEXT"
            },
            {
                "name": "jhtcTimeList",
                "source": "jhtcTimeList",
                "type": "TEXT"
            },
            {
                "name": "jlzbTime",
                "source": "jlzbTime",
                "type": "TEXT"
            },
            {
                "name": "jlzbjhsbTime",
                "source": "jlzbjhsbTime",
                "type": "TEXT"
            },
            {
                "name": "kypfTime",
                "source": "kypfTime",
                "type": "TEXT"
            },
            {
                "name": "kypsyjxdTime",
                "source": "kypsyjxdTime",
                "type": "TEXT"
            },
            {
                "name": "lineQuantity",
                "source": "lineQuantity",
                "type": "INTEGER"
            },
            {
                "name": "mainTransformerQuantity",
                "source": "mainTransformerQuantity",
                "type": "INTEGER"
            },
            {
                "name": "nonConstrDepartmentImpl",
                "source": "nonConstrDepartmentImpl",
                "type": "INTEGER"
            },
            {
                "name": "num",
                "source": "num",
                "type": "TEXT"
            },
            {
                "name": "planNature",
                "source": "planNature",
                "type": "INTEGER"
            },
            {
                "name": "planNatureName",
                "source": "planNatureName",
                "type": "TEXT"
            },
            {
                "name": "planNatureProduct",
                "source": "planNatureProduct",
                "type": "TEXT"
            },
            {
                "name": "planNatureStart",
                "source": "planNatureStart",
                "type": "TEXT"
            },
            {
                "name": "prjCode",
                "source": "prjCode",
                "type": "TEXT"
            },
            {
                "name": "prjName",
                "source": "prjName",
                "type": "TEXT"
            },
            {
                "name": "prodTransCapacity",
                "source": "prodTransCapacity",
                "type": "TEXT"
            },
            {
                "name": "productionLineLength",
                "source": "productionLineLength",
                "type": "TEXT"
            },
            {
                "name": "projectApprovalDocumentNo",
                "source": "projectApprovalDocumentNo",
                "type": "TEXT"
            },
            {
                "name": "projectType",
                "source": "projectType",
                "type": "TEXT"
            },
            {
                "name": "provinceCode",
                "source": "provinceCode",
                "type": "TEXT"
            },
            {
                "name": "provinceName",
                "source": "provinceName",
                "type": "TEXT"
            },
            {
                "name": "provinceProcessId",
                "source": "provinceProcessId",
                "type": "TEXT"
            },
            {
                "name": "sbpfTime",
                "source": "sbpfTime",
                "type": "TEXT"
            },
            {
                "name": "sbysTime",
                "source": "sbysTime",
                "type": "TEXT"
            },
            {
                "name": "sgzbTime",
                "source": "sgzbTime",
                "type": "TEXT"
            },
            {
                "name": "sgzbjhsbTime",
                "source": "sgzbjhsbTime",
                "type": "TEXT"
            },
            {
                "name": "sjjgTime",
                "source": "sjjgTime",
                "type": "TEXT"
            },
            {
                "name": "sjkgTime",
                "source": "sjkgTime",
                "type": "TEXT"
            },
            {
                "name": "sjtcTime",
                "source": "sjtcTime",
                "type": "TEXT"
            },
            {
                "name": "sjzbTime",
                "source": "sjzbTime",
                "type": "TEXT"
            },
            {
                "name": "sjzbjhsbTime",
                "source": "sjzbjhsbTime",
                "type": "TEXT"
            },
            {
                "name": "spwzzbTime",
                "source": "spwzzbTime",
                "type": "TEXT"
            },
            {
                "name": "spwzzbjhsbTime",
                "source": "spwzzbjhsbTime",
                "type": "TEXT"
            },
            {
                "name": "startReadyMonths",
                "source": "startReadyMonths",
                "type": "INTEGER"
            },
            {
                "name": "stypTime",
                "source": "stypTime",
                "type": "TEXT"
            },
            {
                "name": "tjksTime",
                "source": "tjksTime",
                "type": "TEXT"
            },
            {
                "name": "traceId",
                "source": "traceId",
                "type": "TEXT"
            },
            {
                "name": "tsksTime",
                "source": "tsksTime",
                "type": "TEXT"
            },
            {
                "name": "updateTime",
                "source": "updateTime",
                "type": "TEXT"
            },
            {
                "name": "updaterId",
                "source": "updaterId",
                "type": "TEXT"
            },
            {
                "name": "voltageLevel",
                "source": "voltageLevel",
                "type": "TEXT"
            },
            {
                "name": "voltageLevelName",
                "source": "voltageLevelName",
                "type": "TEXT"
            }
        ],
        "dataset_key": "dataset_b648af56",
        "key_candidates": [
            "id",
            "prjCode"
        ],
        "page_name": "年度进度计划分析",
        "parent_record_path": null,
        "partition_field": "prjCode",
        "partition_key": "prjCode",
        "plugin_id": "dcp-dataset-b648af56",
        "record_path": "raw_event",
        "record_type": "yearly_progress_analysis:raw_event",
        "table": "canonical_p020_page_b648af56__yearly_progress_analysis__raw_event"
    },
    {
        "api_name": "yearly_progress_analysis",
        "api_path": "/apit/ebuild2-domain-plan-progress/v1/provincePlanView/queryBeforeAfterDetail",
        "columns": [
            {
                "name": "azksTime",
                "source": "azksTime",
                "type": "TEXT"
            },
            {
                "name": "buildInterval",
                "source": "buildInterval",
                "type": "TEXT"
            },
            {
                "name": "buildProcessId",
                "source": "buildProcessId",
                "type": "TEXT"
            },
            {
                "name": "buildUnitCode",
                "source": "buildUnitCode",
                "type": "TEXT"
            },
            {
                "name": "buildUnitName",
                "source": "buildUnitName",
                "type": "TEXT"
            },
            {
                "name": "cbsjpsTime",
                "source": "cbsjpsTime",
                "type": "TEXT"
            },
            {
                "name": "cbsjpsyjxdTime",
                "source": "cbsjpsyjxdTime",
                "type": "TEXT"
            },
            {
                "name": "constrNature",
                "source": "constrNature",
                "type": "INTEGER"
            },
            {
                "name": "constrNatureName",
                "source": "constrNatureName",
                "type": "TEXT"
            },
            {
                "name": "constrTransformerCapacity",
                "source": "constrTransformerCapacity",
                "type": "REAL"
            },
            {
                "name": "constructionLineLength",
                "source": "constructionLineLength",
                "type": "REAL"
            },
            {
                "name": "createTime",
                "source": "createTime",
                "type": "TEXT"
            },
            {
                "name": "createType",
                "source": "createType",
                "type": "INTEGER"
            },
            {
                "name": "createrId",
                "source": "createrId",
                "type": "TEXT"
            },
            {
                "name": "cspfTime",
                "source": "cspfTime",
                "type": "TEXT"
            },
            {
                "name": "dazlyjTime",
                "source": "dazlyjTime",
                "type": "TEXT"
            },
            {
                "name": "deleteFlag",
                "source": "deleteFlag",
                "type": "INTEGER"
            },
            {
                "name": "extra",
                "source": "extra",
                "type": "TEXT"
            },
            {
                "name": "feaLineLength",
                "source": "feaLineLength",
                "type": "TEXT"
            },
            {
                "name": "feasTransCapacity",
                "source": "feasTransCapacity",
                "type": "TEXT"
            },
            {
                "name": "hbysTime",
                "source": "hbysTime",
                "type": "TEXT"
            },
            {
                "name": "hppfTime",
                "source": "hppfTime",
                "type": "TEXT"
            },
            {
                "name": "hqProcessId",
                "source": "hqProcessId",
                "type": "TEXT"
            },
            {
                "name": "hzTime",
                "source": "hzTime",
                "type": "TEXT"
            },
            {
                "name": "id",
                "source": "id",
                "type": "TEXT"
            },
            {
                "name": "imageProgress",
                "source": "imageProgress",
                "type": "TEXT"
            },
            {
                "name": "investEsti",
                "source": "investEsti",
                "type": "TEXT"
            },
            {
                "name": "jgjsTime",
                "source": "jgjsTime",
                "type": "TEXT"
            },
            {
                "name": "jhjgTime",
                "source": "jhjgTime",
                "type": "TEXT"
            },
            {
                "name": "jhkgTime",
                "source": "jhkgTime",
                "type": "TEXT"
            },
            {
                "name": "jhtcTime",
                "source": "jhtcTime",
                "type": "TEXT"
            },
            {
                "name": "jlzbTime",
                "source": "jlzbTime",
                "type": "TEXT"
            },
            {
                "name": "jlzbjhsbTime",
                "source": "jlzbjhsbTime",
                "type": "TEXT"
            },
            {
                "name": "kypfTime",
                "source": "kypfTime",
                "type": "TEXT"
            },
            {
                "name": "kypsyjxdTime",
                "source": "kypsyjxdTime",
                "type": "TEXT"
            },
            {
                "name": "lineQuantity",
                "source": "lineQuantity",
                "type": "INTEGER"
            },
            {
                "name": "mainTransformerQuantity",
                "source": "mainTransformerQuantity",
                "type": "TEXT"
            },
            {
                "name": "num",
                "source": "num",
                "type": "TEXT"
            },
            {
                "name": "planType",
                "source": "planType",
                "type": "TEXT"
            },
            {
                "name": "prjCode",
                "source": "prjCode",
                "type": "TEXT"
            },
            {
                "name": "prodTransCapacity",
                "source": "prodTransCapacity",
                "type": "TEXT"
            },
            {
                "name": "productionLineLength",
                "source": "productionLineLength",
                "type": "TEXT"
            },
            {
                "name": "prophaseInterval",
                "source": "prophaseInterval",
                "type": "TEXT"
            },
            {
                "name": "provinceCode",
                "source": "provinceCode",
                "type": "TEXT"
            },
            {
                "name": "provinceName",
                "source": "provinceName",
                "type": "TEXT"
            },
            {
                "name": "provinceProcessId",
                "source": "provinceProcessId",
                "type": "TEXT"
            },
            {
                "name": "sbpfTime",
                "source": "sbpfTime",
                "type": "TEXT"
            },
            {
                "name": "sbysTime",
                "source": "sbysTime",
                "type": "TEXT"
            },
            {
                "name": "sgzbTime",
                "source": "sgzbTime",
                "type": "TEXT"
            },
            {
                "name": "sgzbjhsbTime",
                "source": "sgzbjhsbTime",
                "type": "TEXT"
            },
            {
                "name": "singleProjectCode",
                "source": "singleProjectCode",
                "type": "TEXT"
            },
            {
                "name": "singleProjectDetailsType",
                "source": "singleProjectDetailsType",
                "type": "INTEGER"
            },
            {
                "name": "singleProjectDetailsTypeName",
                "source": "singleProjectDetailsTypeName",
                "type": "TEXT"
            },
            {
                "name": "singleProjectName",
                "source": "singleProjectName",
                "type": "TEXT"
            },
            {
                "name": "singleProjectPrerType",
                "source": "singleProjectPrerType",
                "type": "TEXT"
            },
            {
                "name": "singleProjectPrerTypeName",
                "source": "singleProjectPrerTypeName",
                "type": "TEXT"
            },
            {
                "name": "singleProjectType",
                "source": "singleProjectType",
                "type": "INTEGER"
            },
            {
                "name": "singleProjectTypeName",
                "source": "singleProjectTypeName",
                "type": "TEXT"
            },
            {
                "name": "sjjgTime",
                "source": "sjjgTime",
                "type": "TEXT"
            },
            {
                "name": "sjkgTime",
                "source": "sjkgTime",
                "type": "TEXT"
            },
            {
                "name": "sjtcTime",
                "source": "sjtcTime",
                "type": "TEXT"
            },
            {
                "name": "sjzbTime",
                "source": "sjzbTime",
                "type": "TEXT"
            },
            {
                "name": "sjzbjhsbTime",
                "source": "sjzbjhsbTime",
                "type": "TEXT"
            },
            {
                "name": "spwzzbTime",
                "source": "spwzzbTime",
                "type": "TEXT"
            },
            {
                "name": "spwzzbjhsbTime",
                "source": "spwzzbjhsbTime",
                "type": "TEXT"
            },
            {
                "name": "stypTime",
                "source": "stypTime",
                "type": "TEXT"
            },
            {
                "name": "tjksTime",
                "source": "tjksTime",
                "type": "TEXT"
            },
            {
                "name": "traceId",
                "source": "traceId",
                "type": "TEXT"
            },
            {
                "name": "tsksTime",
                "source": "tsksTime",
                "type": "TEXT"
            },
            {
                "name": "updateTime",
                "source": "updateTime",
                "type": "TEXT"
            },
            {
                "name": "updaterId",
                "source": "updaterId",
                "type": "TEXT"
            },
            {
                "name": "voltageLevel",
                "source": "voltageLevel",
                "type": "TEXT"
            },
            {
                "name": "voltageLevelName",
                "source": "voltageLevelName",
                "type": "TEXT"
            }
        ],
        "dataset_key": "dataset_b648af56",
        "key_candidates": [
            "id",
            "prjCode",
            "singleProjectCode",
            "prjCode+singleProjectCode"
        ],
        "page_name": "年度进度计划分析",
        "parent_record_path": "raw_event",
        "partition_field": "prjCode",
        "partition_key": "prjCode",
        "plugin_id": "dcp-dataset-b648af56",
        "record_path": "raw_event.singleList[]",
        "record_type": "yearly_progress_analysis:raw_event.singleList[]",
        "table": "canonical_p020_page_b648af56__yearly_progress_analysis__raw_event_singlelist_items"
    },
    {
        "api_name": "yearly_progress_analysis",
        "api_path": "/apit/ebuild2-domain-plan-progress/v1/provincePlanView/queryBeforeAfterDetail",
        "columns": [
            {
                "name": "detail",
                "source": "detail",
                "type": "TEXT"
            },
            {
                "name": "extra",
                "source": "extra",
                "type": "TEXT"
            },
            {
                "name": "time",
                "source": "time",
                "type": "TEXT"
            },
            {
                "name": "traceId",
                "source": "traceId",
                "type": "TEXT"
            }
        ],
        "dataset_key": "dataset_b648af56",
        "key_candidates": [
            "source_record_key+record_path"
        ],
        "page_name": "年度进度计划分析",
        "parent_record_path": "raw_event",
        "partition_field": null,
        "partition_key": null,
        "plugin_id": "dcp-dataset-b648af56",
        "record_path": "raw_event.constructionLineLengthList[]",
        "record_type": "yearly_progress_analysis:raw_event.constructionLineLengthList[]",
        "table": "canonical_p020_page_b648af56__yearly_progress_analysis__raw_event_constructionlinelengthlist_items"
    },
    {
        "api_name": "queryBuildDetail",
        "api_path": "/apit/ebuild2-domain-plan-progress/v1/provinceProcess/queryBuildDetail",
        "columns": [
            {
                "name": "adjustCause",
                "source": "adjustCause",
                "type": "TEXT"
            },
            {
                "name": "adjustType",
                "source": "adjustType",
                "type": "TEXT"
            },
            {
                "name": "apprFileNo",
                "source": "apprFileNo",
                "type": "TEXT"
            },
            {
                "name": "azksTime",
                "source": "azksTime",
                "type": "TEXT"
            },
            {
                "name": "buildProcessId",
                "source": "buildProcessId",
                "type": "TEXT"
            },
            {
                "name": "buildUnitCode",
                "source": "buildUnitCode",
                "type": "TEXT"
            },
            {
                "name": "buildUnitName",
                "source": "buildUnitName",
                "type": "TEXT"
            },
            {
                "name": "cbStart",
                "source": "cbStart",
                "type": "INTEGER"
            },
            {
                "name": "cbStartName",
                "source": "cbStartName",
                "type": "TEXT"
            },
            {
                "name": "cbsjpsTime",
                "source": "cbsjpsTime",
                "type": "TEXT"
            },
            {
                "name": "cbsjpsyjxdTime",
                "source": "cbsjpsyjxdTime",
                "type": "TEXT"
            },
            {
                "name": "constrAddress",
                "source": "constrAddress",
                "type": "TEXT"
            },
            {
                "name": "constrNature",
                "source": "constrNature",
                "type": "INTEGER"
            },
            {
                "name": "constrNatureName",
                "source": "constrNatureName",
                "type": "TEXT"
            },
            {
                "name": "constrTransformerCapacity",
                "source": "constrTransformerCapacity",
                "type": "REAL"
            },
            {
                "name": "constructionCategory",
                "source": "constructionCategory",
                "type": "INTEGER"
            },
            {
                "name": "constructionCategoryName",
                "source": "constructionCategoryName",
                "type": "TEXT"
            },
            {
                "name": "constructionLineLength",
                "source": "constructionLineLength",
                "type": "REAL"
            },
            {
                "name": "createTime",
                "source": "createTime",
                "type": "TEXT"
            },
            {
                "name": "createType",
                "source": "createType",
                "type": "INTEGER"
            },
            {
                "name": "createrId",
                "source": "createrId",
                "type": "TEXT"
            },
            {
                "name": "cspfTime",
                "source": "cspfTime",
                "type": "TEXT"
            },
            {
                "name": "currentBudget",
                "source": "currentBudget",
                "type": "REAL"
            },
            {
                "name": "currentInvestment",
                "source": "currentInvestment",
                "type": "REAL"
            },
            {
                "name": "dazlyjTime",
                "source": "dazlyjTime",
                "type": "TEXT"
            },
            {
                "name": "deleteFlag",
                "source": "deleteFlag",
                "type": "INTEGER"
            },
            {
                "name": "durationMonths",
                "source": "durationMonths",
                "type": "INTEGER"
            },
            {
                "name": "extra",
                "source": "extra",
                "type": "TEXT"
            },
            {
                "name": "feaDinvest",
                "source": "feaDinvest",
                "type": "TEXT"
            },
            {
                "name": "feaLineLength",
                "source": "feaLineLength",
                "type": "TEXT"
            },
            {
                "name": "feaSinvest",
                "source": "feaSinvest",
                "type": "TEXT"
            },
            {
                "name": "feasTransCapacity",
                "source": "feasTransCapacity",
                "type": "TEXT"
            },
            {
                "name": "hbysTime",
                "source": "hbysTime",
                "type": "TEXT"
            },
            {
                "name": "hppfTime",
                "source": "hppfTime",
                "type": "TEXT"
            },
            {
                "name": "hqProcessId",
                "source": "hqProcessId",
                "type": "TEXT"
            },
            {
                "name": "hzTime",
                "source": "hzTime",
                "type": "TEXT"
            },
            {
                "name": "id",
                "source": "id",
                "type": "TEXT"
            },
            {
                "name": "imageProgress",
                "source": "imageProgress",
                "type": "TEXT"
            },
            {
                "name": "investEsti",
                "source": "investEsti",
                "type": "TEXT"
            },
            {
                "name": "jgjsTime",
                "source": "jgjsTime",
                "type": "TEXT"
            },
            {
                "name": "jhjgTime",
                "source": "jhjgTime",
                "type": "TEXT"
            },
            {
                "name": "jhkgTime",
                "source": "jhkgTime",
                "type": "TEXT"
            },
            {
                "name": "jhtcTime",
                "source": "jhtcTime",
                "type": "TEXT"
            },
            {
                "name": "jlzbTime",
                "source": "jlzbTime",
                "type": "TEXT"
            },
            {
                "name": "jlzbjhsbTime",
                "source": "jlzbjhsbTime",
                "type": "TEXT"
            },
            {
                "name": "kypfTime",
                "source": "kypfTime",
                "type": "TEXT"
            },
            {
                "name": "kypsyjxdTime",
                "source": "kypsyjxdTime",
                "type": "TEXT"
            },
            {
                "name": "lineQuantity",
                "source": "lineQuantity",
                "type": "INTEGER"
            },
            {
                "name": "mainTransformerQuantity",
                "source": "mainTransformerQuantity",
                "type": "INTEGER"
            },
            {
                "name": "nonConstrDepartmentImpl",
                "source": "nonConstrDepartmentImpl",
                "type": "INTEGER"
            },
            {
                "name": "num",
                "source": "num",
                "type": "TEXT"
            },
            {
                "name": "planNatureProduct",
                "source": "planNatureProduct",
                "type": "TEXT"
            },
            {
                "name": "planNatureStart",
                "source": "planNatureStart",
                "type": "TEXT"
            },
            {
                "name": "prjCode",
                "source": "prjCode",
                "type": "TEXT"
            },
            {
                "name": "prjName",
                "source": "prjName",
                "type": "TEXT"
            },
            {
                "name": "prodTransCapacity",
                "source": "prodTransCapacity",
                "type": "TEXT"
            },
            {
                "name": "productionLineLength",
                "source": "productionLineLength",
                "type": "TEXT"
            },
            {
                "name": "projectApprovalDocumentNo",
                "source": "projectApprovalDocumentNo",
                "type": "TEXT"
            },
            {
                "name": "projectType",
                "source": "projectType",
                "type": "TEXT"
            },
            {
                "name": "provinceCode",
                "source": "provinceCode",
                "type": "TEXT"
            },
            {
                "name": "provinceName",
                "source": "provinceName",
                "type": "TEXT"
            },
            {
                "name": "provinceProcessId",
                "source": "provinceProcessId",
                "type": "TEXT"
            },
            {
                "name": "sbpfTime",
                "source": "sbpfTime",
                "type": "TEXT"
            },
            {
                "name": "sbysTime",
                "source": "sbysTime",
                "type": "TEXT"
            },
            {
                "name": "sgzbTime",
                "source": "sgzbTime",
                "type": "TEXT"
            },
            {
                "name": "sgzbjhsbTime",
                "source": "sgzbjhsbTime",
                "type": "TEXT"
            },
            {
                "name": "sjjgTime",
                "source": "sjjgTime",
                "type": "TEXT"
            },
            {
                "name": "sjkgTime",
                "source": "sjkgTime",
                "type": "TEXT"
            },
            {
                "name": "sjtcTime",
                "source": "sjtcTime",
                "type": "TEXT"
            },
            {
                "name": "sjzbTime",
                "source": "sjzbTime",
                "type": "TEXT"
            },
            {
                "name": "sjzbjhsbTime",
                "source": "sjzbjhsbTime",
                "type": "TEXT"
            },
            {
                "name": "spwzzbTime",
                "source": "spwzzbTime",
                "type": "TEXT"
            },
            {
                "name": "spwzzbjhsbTime",
                "source": "spwzzbjhsbTime",
                "type": "TEXT"
            },
            {
                "name": "startReadyMonths",
                "source": "startReadyMonths",
                "type": "INTEGER"
            },
            {
                "name": "stypTime",
                "source": "stypTime",
                "type": "TEXT"
            },
            {
                "name": "tjksTime",
                "source": "tjksTime",
                "type": "TEXT"
            },
            {
                "name": "traceId",
                "source": "traceId",
                "type": "TEXT"
            },
            {
                "name": "tsksTime",
                "source": "tsksTime",
                "type": "TEXT"
            },
            {
                "name": "updateTime",
                "source": "updateTime",
                "type": "TEXT"
            },
            {
                "name": "updaterId",
                "source": "updaterId",
                "type": "TEXT"
            },
            {
                "name": "voltageLevel",
                "source": "voltageLevel",
                "type": "TEXT"
            },
            {
                "name": "voltageLevelName",
                "source": "voltageLevelName",
                "type": "TEXT"
            }
        ],
        "dataset_key": "dataset_456bbe0b",
        "key_candidates": [
            "id",
            "prjCode"
        ],
        "page_name": "年度进度计划编制",
        "parent_record_path": null,
        "partition_field": "prjCode",
        "partition_key": "prjCode",
        "plugin_id": "dcp-dataset-456bbe0b",
        "record_path": "raw_event",
        "record_type": "queryBuildDetail:raw_event",
        "table": "canonical_p021_page_456bbe0b__querybuilddetail__raw_event"
    },
    {
        "api_name": "queryBuildDetail",
        "api_path": "/apit/ebuild2-domain-plan-progress/v1/provinceProcess/queryBuildDetail",
        "columns": [
            {
                "name": "azksTime",
                "source": "azksTime",
                "type": "TEXT"
            },
            {
                "name": "buildInterval",
                "source": "buildInterval",
                "type": "TEXT"
            },
            {
                "name": "buildProcessId",
                "source": "buildProcessId",
                "type": "TEXT"
            },
            {
                "name": "buildUnitCode",
                "source": "buildUnitCode",
                "type": "TEXT"
            },
            {
                "name": "buildUnitName",
                "source": "buildUnitName",
                "type": "TEXT"
            },
            {
                "name": "cbsjpsTime",
                "source": "cbsjpsTime",
                "type": "TEXT"
            },
            {
                "name": "cbsjpsyjxdTime",
                "source": "cbsjpsyjxdTime",
                "type": "TEXT"
            },
            {
                "name": "constrNature",
                "source": "constrNature",
                "type": "INTEGER"
            },
            {
                "name": "constrNatureName",
                "source": "constrNatureName",
                "type": "TEXT"
            },
            {
                "name": "constrTransformerCapacity",
                "source": "constrTransformerCapacity",
                "type": "REAL"
            },
            {
                "name": "constructionLineLength",
                "source": "constructionLineLength",
                "type": "REAL"
            },
            {
                "name": "createTime",
                "source": "createTime",
                "type": "TEXT"
            },
            {
                "name": "createType",
                "source": "createType",
                "type": "INTEGER"
            },
            {
                "name": "createrId",
                "source": "createrId",
                "type": "TEXT"
            },
            {
                "name": "cspfTime",
                "source": "cspfTime",
                "type": "TEXT"
            },
            {
                "name": "dazlyjTime",
                "source": "dazlyjTime",
                "type": "TEXT"
            },
            {
                "name": "deleteFlag",
                "source": "deleteFlag",
                "type": "INTEGER"
            },
            {
                "name": "extra",
                "source": "extra",
                "type": "TEXT"
            },
            {
                "name": "feaLineLength",
                "source": "feaLineLength",
                "type": "TEXT"
            },
            {
                "name": "feasTransCapacity",
                "source": "feasTransCapacity",
                "type": "TEXT"
            },
            {
                "name": "hbysTime",
                "source": "hbysTime",
                "type": "TEXT"
            },
            {
                "name": "hppfTime",
                "source": "hppfTime",
                "type": "TEXT"
            },
            {
                "name": "hqProcessId",
                "source": "hqProcessId",
                "type": "TEXT"
            },
            {
                "name": "hzTime",
                "source": "hzTime",
                "type": "TEXT"
            },
            {
                "name": "id",
                "source": "id",
                "type": "TEXT"
            },
            {
                "name": "imageProgress",
                "source": "imageProgress",
                "type": "TEXT"
            },
            {
                "name": "investEsti",
                "source": "investEsti",
                "type": "TEXT"
            },
            {
                "name": "jgjsTime",
                "source": "jgjsTime",
                "type": "TEXT"
            },
            {
                "name": "jhjgTime",
                "source": "jhjgTime",
                "type": "TEXT"
            },
            {
                "name": "jhkgTime",
                "source": "jhkgTime",
                "type": "TEXT"
            },
            {
                "name": "jhtcTime",
                "source": "jhtcTime",
                "type": "TEXT"
            },
            {
                "name": "jlzbTime",
                "source": "jlzbTime",
                "type": "TEXT"
            },
            {
                "name": "jlzbjhsbTime",
                "source": "jlzbjhsbTime",
                "type": "TEXT"
            },
            {
                "name": "kypfTime",
                "source": "kypfTime",
                "type": "TEXT"
            },
            {
                "name": "kypsyjxdTime",
                "source": "kypsyjxdTime",
                "type": "TEXT"
            },
            {
                "name": "lineQuantity",
                "source": "lineQuantity",
                "type": "INTEGER"
            },
            {
                "name": "mainTransformerQuantity",
                "source": "mainTransformerQuantity",
                "type": "INTEGER"
            },
            {
                "name": "num",
                "source": "num",
                "type": "TEXT"
            },
            {
                "name": "planType",
                "source": "planType",
                "type": "TEXT"
            },
            {
                "name": "prjCode",
                "source": "prjCode",
                "type": "TEXT"
            },
            {
                "name": "prodTransCapacity",
                "source": "prodTransCapacity",
                "type": "TEXT"
            },
            {
                "name": "productionLineLength",
                "source": "productionLineLength",
                "type": "TEXT"
            },
            {
                "name": "prophaseInterval",
                "source": "prophaseInterval",
                "type": "TEXT"
            },
            {
                "name": "provinceCode",
                "source": "provinceCode",
                "type": "TEXT"
            },
            {
                "name": "provinceName",
                "source": "provinceName",
                "type": "TEXT"
            },
            {
                "name": "provinceProcessId",
                "source": "provinceProcessId",
                "type": "TEXT"
            },
            {
                "name": "sbpfTime",
                "source": "sbpfTime",
                "type": "TEXT"
            },
            {
                "name": "sbysTime",
                "source": "sbysTime",
                "type": "TEXT"
            },
            {
                "name": "sgzbTime",
                "source": "sgzbTime",
                "type": "TEXT"
            },
            {
                "name": "sgzbjhsbTime",
                "source": "sgzbjhsbTime",
                "type": "TEXT"
            },
            {
                "name": "singleProjectCode",
                "source": "singleProjectCode",
                "type": "TEXT"
            },
            {
                "name": "singleProjectDetailsType",
                "source": "singleProjectDetailsType",
                "type": "INTEGER"
            },
            {
                "name": "singleProjectDetailsTypeName",
                "source": "singleProjectDetailsTypeName",
                "type": "TEXT"
            },
            {
                "name": "singleProjectName",
                "source": "singleProjectName",
                "type": "TEXT"
            },
            {
                "name": "singleProjectPrerType",
                "source": "singleProjectPrerType",
                "type": "TEXT"
            },
            {
                "name": "singleProjectPrerTypeName",
                "source": "singleProjectPrerTypeName",
                "type": "TEXT"
            },
            {
                "name": "singleProjectType",
                "source": "singleProjectType",
                "type": "INTEGER"
            },
            {
                "name": "singleProjectTypeName",
                "source": "singleProjectTypeName",
                "type": "TEXT"
            },
            {
                "name": "sjjgTime",
                "source": "sjjgTime",
                "type": "TEXT"
            },
            {
                "name": "sjkgTime",
                "source": "sjkgTime",
                "type": "TEXT"
            },
            {
                "name": "sjtcTime",
                "source": "sjtcTime",
                "type": "TEXT"
            },
            {
                "name": "sjzbTime",
                "source": "sjzbTime",
                "type": "TEXT"
            },
            {
                "name": "sjzbjhsbTime",
                "source": "sjzbjhsbTime",
                "type": "TEXT"
            },
            {
                "name": "spwzzbTime",
                "source": "spwzzbTime",
                "type": "TEXT"
            },
            {
                "name": "spwzzbjhsbTime",
                "source": "spwzzbjhsbTime",
                "type": "TEXT"
            },
            {
                "name": "stypTime",
                "source": "stypTime",
                "type": "TEXT"
            },
            {
                "name": "tjksTime",
                "source": "tjksTime",
                "type": "TEXT"
            },
            {
                "name": "traceId",
                "source": "traceId",
                "type": "TEXT"
            },
            {
                "name": "tsksTime",
                "source": "tsksTime",
                "type": "TEXT"
            },
            {
                "name": "updateTime",
                "source": "updateTime",
                "type": "TEXT"
            },
            {
                "name": "updaterId",
                "source": "updaterId",
                "type": "TEXT"
            },
            {
                "name": "voltageLevel",
                "source": "voltageLevel",
                "type": "TEXT"
            },
            {
                "name": "voltageLevelName",
                "source": "voltageLevelName",
                "type": "TEXT"
            }
        ],
        "dataset_key": "dataset_456bbe0b",
        "key_candidates": [
            "id",
            "prjCode",
            "singleProjectCode",
            "prjCode+singleProjectCode"
        ],
        "page_name": "年度进度计划编制",
        "parent_record_path": "raw_event",
        "partition_field": "prjCode",
        "partition_key": "prjCode",
        "plugin_id": "dcp-dataset-456bbe0b",
        "record_path": "raw_event.singleList[]",
        "record_type": "queryBuildDetail:raw_event.singleList[]",
        "table": "canonical_p021_page_456bbe0b__querybuilddetail__raw_event_singlelist_items"
    },
    {
        "api_name": "commencement_report_create_form",
        "api_path": "/apit/ebuild2-domain-project-stage/v1/commenAppInfo/createDS",
        "columns": [
            {
                "name": "applicationCommenDate",
                "source": "applicationCommenDate",
                "type": "TEXT"
            },
            {
                "name": "applicationNo",
                "source": "applicationNo",
                "type": "TEXT"
            },
            {
                "name": "bidSectNameOnBidSect",
                "source": "bidSectNameOnBidSect",
                "type": "TEXT"
            },
            {
                "name": "biddingSectionCode",
                "source": "biddingSectionCode",
                "type": "TEXT"
            },
            {
                "name": "biddingSectionName",
                "source": "biddingSectionName",
                "type": "TEXT"
            },
            {
                "name": "bpmId",
                "source": "bpmId",
                "type": "TEXT"
            },
            {
                "name": "buildUnitApprOpinion",
                "source": "buildUnitApprOpinion",
                "type": "TEXT"
            },
            {
                "name": "buildUnitApprTime",
                "source": "buildUnitApprTime",
                "type": "TEXT"
            },
            {
                "name": "buildUnitCode",
                "source": "buildUnitCode",
                "type": "TEXT"
            },
            {
                "name": "buildUnitName",
                "source": "buildUnitName",
                "type": "TEXT"
            },
            {
                "name": "constrDeptName",
                "source": "constrDeptName",
                "type": "TEXT"
            },
            {
                "name": "constrId",
                "source": "constrId",
                "type": "TEXT"
            },
            {
                "name": "constrNature",
                "source": "constrNature",
                "type": "INTEGER"
            },
            {
                "name": "constrNatureText",
                "source": "constrNatureText",
                "type": "TEXT"
            },
            {
                "name": "constrTransCapacity",
                "source": "constrTransCapacity",
                "type": "REAL"
            },
            {
                "name": "construcApprTime",
                "source": "construcApprTime",
                "type": "TEXT"
            },
            {
                "name": "currentDisposeId",
                "source": "currentDisposeId",
                "type": "TEXT"
            },
            {
                "name": "fileId",
                "source": "fileId",
                "type": "TEXT"
            },
            {
                "name": "flowRole",
                "source": "flowRole",
                "type": "INTEGER"
            },
            {
                "name": "id",
                "source": "id",
                "type": "TEXT"
            },
            {
                "name": "instanceId",
                "source": "instanceId",
                "type": "TEXT"
            },
            {
                "name": "isCanRecall",
                "source": "isCanRecall",
                "type": "INTEGER"
            },
            {
                "name": "itemUnderReview",
                "source": "itemUnderReview",
                "type": "TEXT"
            },
            {
                "name": "operatorFlag",
                "source": "operatorFlag",
                "type": "INTEGER"
            },
            {
                "name": "operatorFlagS",
                "source": "operatorFlagS",
                "type": "TEXT"
            },
            {
                "name": "ownerApprovalOpinion",
                "source": "ownerApprovalOpinion",
                "type": "TEXT"
            },
            {
                "name": "ownerApprovalTime",
                "source": "ownerApprovalTime",
                "type": "TEXT"
            },
            {
                "name": "ownerDeptName",
                "source": "ownerDeptName",
                "type": "TEXT"
            },
            {
                "name": "ownerDeptNo",
                "source": "ownerDeptNo",
                "type": "TEXT"
            },
            {
                "name": "ownerId",
                "source": "ownerId",
                "type": "TEXT"
            },
            {
                "name": "prjCode",
                "source": "prjCode",
                "type": "TEXT"
            },
            {
                "name": "prjManageMode",
                "source": "prjManageMode",
                "type": "INTEGER"
            },
            {
                "name": "prjName",
                "source": "prjName",
                "type": "TEXT"
            },
            {
                "name": "proImpPlanRecFileId",
                "source": "proImpPlanRecFileId",
                "type": "TEXT"
            },
            {
                "name": "proImpPlanRecFileName",
                "source": "proImpPlanRecFileName",
                "type": "TEXT"
            },
            {
                "name": "processFlag",
                "source": "processFlag",
                "type": "INTEGER"
            },
            {
                "name": "projectName",
                "source": "projectName",
                "type": "TEXT"
            },
            {
                "name": "projectType",
                "source": "projectType",
                "type": "INTEGER"
            },
            {
                "name": "provinceApprOpinion",
                "source": "provinceApprOpinion",
                "type": "TEXT"
            },
            {
                "name": "provinceApprTime",
                "source": "provinceApprTime",
                "type": "TEXT"
            },
            {
                "name": "provinceApprUserId",
                "source": "provinceApprUserId",
                "type": "TEXT"
            },
            {
                "name": "provinceCode",
                "source": "provinceCode",
                "type": "TEXT"
            },
            {
                "name": "provinceName",
                "source": "provinceName",
                "type": "TEXT"
            },
            {
                "name": "remark",
                "source": "remark",
                "type": "TEXT"
            },
            {
                "name": "reviewStatus",
                "source": "reviewStatus",
                "type": "INTEGER"
            },
            {
                "name": "seeFlag",
                "source": "seeFlag",
                "type": "INTEGER"
            },
            {
                "name": "signatureList",
                "source": "signatureList",
                "type": "TEXT"
            },
            {
                "name": "signatureNO",
                "source": "signatureNO",
                "type": "TEXT"
            },
            {
                "name": "signaturesStatus",
                "source": "signaturesStatus",
                "type": "INTEGER"
            },
            {
                "name": "singleProjectCode",
                "source": "singleProjectCode",
                "type": "TEXT"
            },
            {
                "name": "singleProjectName",
                "source": "singleProjectName",
                "type": "TEXT"
            },
            {
                "name": "singleProjectType",
                "source": "singleProjectType",
                "type": "INTEGER"
            },
            {
                "name": "singleProjectTypeText",
                "source": "singleProjectTypeText",
                "type": "TEXT"
            },
            {
                "name": "supervisionDeptName",
                "source": "supervisionDeptName",
                "type": "TEXT"
            },
            {
                "name": "supervisorApprOpinion",
                "source": "supervisorApprOpinion",
                "type": "TEXT"
            },
            {
                "name": "supervisorApprTime",
                "source": "supervisorApprTime",
                "type": "TEXT"
            },
            {
                "name": "supervisorDeptNo",
                "source": "supervisorDeptNo",
                "type": "TEXT"
            },
            {
                "name": "supervisorId",
                "source": "supervisorId",
                "type": "TEXT"
            },
            {
                "name": "volLevel",
                "source": "volLevel",
                "type": "TEXT"
            },
            {
                "name": "volLevel1",
                "source": "volLevel1",
                "type": "TEXT"
            }
        ],
        "dataset_key": "dataset_8975c58e",
        "key_candidates": [
            "id",
            "prjCode",
            "singleProjectCode",
            "biddingSectionCode",
            "prjCode+singleProjectCode+biddingSectionCode"
        ],
        "page_name": "开工报审",
        "parent_record_path": null,
        "partition_field": "prjCode",
        "partition_key": "prjCode",
        "plugin_id": "dcp-dataset-8975c58e",
        "record_path": "raw_event",
        "record_type": "commencement_report_create_form:raw_event",
        "table": "canonical_p022_page_8975c58e__commencement_report_create_form__raw_event"
    },
    {
        "api_name": "getDrawProcessPicForApp",
        "api_path": "/apit/ebuild2-agg-frame-workbench/v1/worktask/getDrawProcessPicForApp",
        "columns": [
            {
                "name": "activityDefID",
                "source": "activityDefID",
                "type": "TEXT"
            },
            {
                "name": "activityInstID",
                "source": "activityInstID",
                "type": "TEXT"
            },
            {
                "name": "activityInstName",
                "source": "activityInstName",
                "type": "TEXT"
            },
            {
                "name": "approveOpinion",
                "source": "approveOpinion",
                "type": "TEXT"
            },
            {
                "name": "businessID",
                "source": "businessID",
                "type": "TEXT"
            },
            {
                "name": "dataType",
                "source": "dataType",
                "type": "TEXT"
            },
            {
                "name": "isComplate",
                "source": "isComplate",
                "type": "TEXT"
            },
            {
                "name": "isRead",
                "source": "isRead",
                "type": "TEXT"
            },
            {
                "name": "lastModifyDate",
                "source": "lastModifyDate",
                "type": "TEXT"
            },
            {
                "name": "nodeName",
                "source": "nodeName",
                "type": "TEXT"
            },
            {
                "name": "operationDesc",
                "source": "operationDesc",
                "type": "TEXT"
            },
            {
                "name": "operatorName",
                "source": "operatorName",
                "type": "TEXT"
            },
            {
                "name": "orgName",
                "source": "orgName",
                "type": "TEXT"
            },
            {
                "name": "partiId",
                "source": "partiId",
                "type": "TEXT"
            },
            {
                "name": "partiName",
                "source": "partiName",
                "type": "TEXT"
            },
            {
                "name": "priority",
                "source": "priority",
                "type": "TEXT"
            },
            {
                "name": "processDefId",
                "source": "processDefId",
                "type": "TEXT"
            },
            {
                "name": "processInstID",
                "source": "processInstID",
                "type": "TEXT"
            },
            {
                "name": "processStatusCode",
                "source": "processStatusCode",
                "type": "TEXT"
            },
            {
                "name": "roleName",
                "source": "roleName",
                "type": "TEXT"
            },
            {
                "name": "workItemId",
                "source": "workItemId",
                "type": "TEXT"
            }
        ],
        "dataset_key": "dataset_8975c58e",
        "key_candidates": [
            "source_record_key+record_path"
        ],
        "page_name": "开工报审",
        "parent_record_path": null,
        "partition_field": null,
        "partition_key": null,
        "plugin_id": "dcp-dataset-8975c58e",
        "record_path": "raw_event",
        "record_type": "getDrawProcessPicForApp:raw_event",
        "table": "canonical_p022_page_8975c58e__getdrawprocesspicforapp__raw_event"
    },
    {
        "api_name": "getDrawProcessPicForApp",
        "api_path": "/apit/ebuild2-agg-frame-workbench/v1/worktask/getDrawProcessPicForApp",
        "columns": [
            {
                "name": "id",
                "source": "id",
                "type": "TEXT"
            },
            {
                "name": "name",
                "source": "name",
                "type": "TEXT"
            },
            {
                "name": "roleCode",
                "source": "roleCode",
                "type": "TEXT"
            },
            {
                "name": "roleName",
                "source": "roleName",
                "type": "TEXT"
            },
            {
                "name": "typeCode",
                "source": "typeCode",
                "type": "TEXT"
            }
        ],
        "dataset_key": "dataset_8975c58e",
        "key_candidates": [
            "id"
        ],
        "page_name": "开工报审",
        "parent_record_path": "raw_event",
        "partition_field": null,
        "partition_key": null,
        "plugin_id": "dcp-dataset-8975c58e",
        "record_path": "raw_event.participantList[]",
        "record_type": "getDrawProcessPicForApp:raw_event.participantList[]",
        "table": "canonical_p022_page_8975c58e__getdrawprocesspicforapp__raw_event_participantlist_items"
    },
    {
        "api_name": "getDrawProcessPicForApp",
        "api_path": "/apit/ebuild2-agg-frame-workbench/v1/worktask/getDrawProcessPicForApp",
        "columns": [
            {
                "name": "operationDesc",
                "source": "operationDesc",
                "type": "TEXT"
            },
            {
                "name": "operationTime",
                "source": "operationTime",
                "type": "TEXT"
            },
            {
                "name": "processStatusCode",
                "source": "processStatusCode",
                "type": "TEXT"
            }
        ],
        "dataset_key": "dataset_8975c58e",
        "key_candidates": [
            "source_record_key+record_path"
        ],
        "page_name": "开工报审",
        "parent_record_path": "raw_event.participantList[]",
        "partition_field": null,
        "partition_key": null,
        "plugin_id": "dcp-dataset-8975c58e",
        "record_path": "raw_event.participantList[].childRecordList[]",
        "record_type": "getDrawProcessPicForApp:raw_event.participantList[].childRecordList[]",
        "table": "canonical_p022_page_8975c58e__getdrawprocesspicforapp__raw_event_participantlist_items_childrecordlist_"
    },
    {
        "api_name": "getDrawProcessPicForApp",
        "api_path": "/apit/ebuild2-agg-frame-workbench/v1/worktask/getDrawProcessPicForApp",
        "columns": [
            {
                "name": "operationDesc",
                "source": "operationDesc",
                "type": "TEXT"
            },
            {
                "name": "operationTime",
                "source": "operationTime",
                "type": "TEXT"
            },
            {
                "name": "processStatusCode",
                "source": "processStatusCode",
                "type": "TEXT"
            }
        ],
        "dataset_key": "dataset_8975c58e",
        "key_candidates": [
            "source_record_key+record_path"
        ],
        "page_name": "开工报审",
        "parent_record_path": "raw_event",
        "partition_field": null,
        "partition_key": null,
        "plugin_id": "dcp-dataset-8975c58e",
        "record_path": "raw_event.childRecordList[]",
        "record_type": "getDrawProcessPicForApp:raw_event.childRecordList[]",
        "table": "canonical_p022_page_8975c58e__getdrawprocesspicforapp__raw_event_childrecordlist_items"
    },
    {
        "api_name": "technical_scheme_list",
        "api_path": "/apit/ebuild2-domain-security-risk/v1/mainTechnicalScheme/queryMainTechnicalSchemePage",
        "columns": [
            {
                "name": "consequenceDueToRisk",
                "source": "consequenceDueToRisk",
                "type": "TEXT"
            },
            {
                "name": "deleteFlag",
                "source": "deleteFlag",
                "type": "INTEGER"
            },
            {
                "name": "droMeasure",
                "source": "droMeasure",
                "type": "TEXT"
            },
            {
                "name": "droRiskLevel",
                "source": "droRiskLevel",
                "type": "INTEGER"
            },
            {
                "name": "expertArgumentFlag",
                "source": "expertArgumentFlag",
                "type": "INTEGER"
            },
            {
                "name": "extra",
                "source": "extra",
                "type": "TEXT"
            },
            {
                "name": "id",
                "source": "id",
                "type": "TEXT"
            },
            {
                "name": "professional",
                "source": "professional",
                "type": "TEXT"
            },
            {
                "name": "remark",
                "source": "remark",
                "type": "TEXT"
            },
            {
                "name": "riskLevel",
                "source": "riskLevel",
                "type": "INTEGER"
            },
            {
                "name": "riskNo",
                "source": "riskNo",
                "type": "TEXT"
            },
            {
                "name": "schemeType",
                "source": "schemeType",
                "type": "TEXT"
            },
            {
                "name": "singleProjectCode",
                "source": "singleProjectCode",
                "type": "TEXT"
            },
            {
                "name": "singleProjectName",
                "source": "singleProjectName",
                "type": "TEXT"
            },
            {
                "name": "traceId",
                "source": "traceId",
                "type": "TEXT"
            },
            {
                "name": "workContent",
                "source": "workContent",
                "type": "TEXT"
            },
            {
                "name": "workProcedure",
                "source": "workProcedure",
                "type": "TEXT"
            },
            {
                "name": "workSiteId",
                "source": "workSiteId",
                "type": "TEXT"
            },
            {
                "name": "workSiteName",
                "source": "workSiteName",
                "type": "TEXT"
            },
            {
                "name": "workSiteType",
                "source": "workSiteType",
                "type": "TEXT"
            }
        ],
        "dataset_key": "dataset_9c627a89",
        "key_candidates": [
            "id",
            "singleProjectCode"
        ],
        "page_name": "技术方案一览表",
        "parent_record_path": null,
        "partition_field": "singleProjectCode",
        "partition_key": "singleProjectCode",
        "plugin_id": "dcp-dataset-9c627a89",
        "record_path": "raw_event",
        "record_type": "technical_scheme_list:raw_event",
        "table": "canonical_p024_page_9c627a89__technical_scheme_list__raw_event"
    },
    {
        "api_name": "queryConstructionDeptList",
        "api_path": "/apit/ebuild2-domain-project-form/v1/constructionPersonnelChange/queryConstructionDeptList",
        "columns": [
            {
                "name": "address",
                "source": "address",
                "type": "TEXT"
            },
            {
                "name": "affiliationCode",
                "source": "affiliationCode",
                "type": "TEXT"
            },
            {
                "name": "affiliationName",
                "source": "affiliationName",
                "type": "TEXT"
            },
            {
                "name": "bpmId",
                "source": "bpmId",
                "type": "TEXT"
            },
            {
                "name": "buildUnitCode",
                "source": "buildUnitCode",
                "type": "TEXT"
            },
            {
                "name": "contactTelephone",
                "source": "contactTelephone",
                "type": "TEXT"
            },
            {
                "name": "createTime",
                "source": "createTime",
                "type": "INTEGER"
            },
            {
                "name": "createrId",
                "source": "createrId",
                "type": "TEXT"
            },
            {
                "name": "deleteFlag",
                "source": "deleteFlag",
                "type": "INTEGER"
            },
            {
                "name": "departmentStatus",
                "source": "departmentStatus",
                "type": "INTEGER"
            },
            {
                "name": "departmentType",
                "source": "departmentType",
                "type": "INTEGER"
            },
            {
                "name": "deptCitiesCode",
                "source": "deptCitiesCode",
                "type": "INTEGER"
            },
            {
                "name": "deptCitiesName",
                "source": "deptCitiesName",
                "type": "TEXT"
            },
            {
                "name": "deptDistrictCode",
                "source": "deptDistrictCode",
                "type": "INTEGER"
            },
            {
                "name": "deptDistrictName",
                "source": "deptDistrictName",
                "type": "TEXT"
            },
            {
                "name": "deptId",
                "source": "deptId",
                "type": "TEXT"
            },
            {
                "name": "deptProvinceCode",
                "source": "deptProvinceCode",
                "type": "INTEGER"
            },
            {
                "name": "deptProvinceName",
                "source": "deptProvinceName",
                "type": "TEXT"
            },
            {
                "name": "emailAddress",
                "source": "emailAddress",
                "type": "TEXT"
            },
            {
                "name": "establishmentDate",
                "source": "establishmentDate",
                "type": "TEXT"
            },
            {
                "name": "extra",
                "source": "extra",
                "type": "TEXT"
            },
            {
                "name": "faxNo",
                "source": "faxNo",
                "type": "TEXT"
            },
            {
                "name": "groupMarkup",
                "source": "groupMarkup",
                "type": "TEXT"
            },
            {
                "name": "historyFlag",
                "source": "historyFlag",
                "type": "INTEGER"
            },
            {
                "name": "isHaveReset",
                "source": "isHaveReset",
                "type": "TEXT"
            },
            {
                "name": "personnelId",
                "source": "personnelId",
                "type": "TEXT"
            },
            {
                "name": "postalCode",
                "source": "postalCode",
                "type": "TEXT"
            },
            {
                "name": "prjManageMode",
                "source": "prjManageMode",
                "type": "TEXT"
            },
            {
                "name": "projectDepartmentName",
                "source": "projectDepartmentName",
                "type": "TEXT"
            },
            {
                "name": "projectDeptNo",
                "source": "projectDeptNo",
                "type": "TEXT"
            },
            {
                "name": "provinceCode",
                "source": "provinceCode",
                "type": "TEXT"
            },
            {
                "name": "realName",
                "source": "realName",
                "type": "TEXT"
            },
            {
                "name": "singnFlag",
                "source": "singnFlag",
                "type": "TEXT"
            },
            {
                "name": "traceId",
                "source": "traceId",
                "type": "TEXT"
            },
            {
                "name": "updateTime",
                "source": "updateTime",
                "type": "INTEGER"
            },
            {
                "name": "updaterId",
                "source": "updaterId",
                "type": "TEXT"
            },
            {
                "name": "year",
                "source": "year",
                "type": "TEXT"
            }
        ],
        "dataset_key": "dataset_7dd4ed20",
        "key_candidates": [
            "source_record_key+record_path"
        ],
        "page_name": "施工人员管理",
        "parent_record_path": null,
        "partition_field": null,
        "partition_key": null,
        "plugin_id": "dcp-dataset-7dd4ed20",
        "record_path": "raw_event",
        "record_type": "queryConstructionDeptList:raw_event",
        "table": "canonical_p025_page_7dd4ed20__queryconstructiondeptlist__raw_event"
    },
    {
        "api_name": "work_ticket",
        "api_path": "/apit/ebuild2-domain-security-work/v1/constrWorkTicket/queryConstrWorkTicketPagePc",
        "columns": [
            {
                "name": "assessmentRiskLevel",
                "source": "assessmentRiskLevel",
                "type": "INTEGER"
            },
            {
                "name": "auditHierarchy",
                "source": "auditHierarchy",
                "type": "TEXT"
            },
            {
                "name": "bhMeasuresContent",
                "source": "bhMeasuresContent",
                "type": "TEXT"
            },
            {
                "name": "bhSituationContent",
                "source": "bhSituationContent",
                "type": "TEXT"
            },
            {
                "name": "biddingSectionCode",
                "source": "biddingSectionCode",
                "type": "TEXT"
            },
            {
                "name": "biddingSectionName",
                "source": "biddingSectionName",
                "type": "TEXT"
            },
            {
                "name": "buildUnitCode",
                "source": "buildUnitCode",
                "type": "TEXT"
            },
            {
                "name": "buildUnitName",
                "source": "buildUnitName",
                "type": "TEXT"
            },
            {
                "name": "city",
                "source": "city",
                "type": "TEXT"
            },
            {
                "name": "constructionHeadcount",
                "source": "constructionHeadcount",
                "type": "TEXT"
            },
            {
                "name": "constructionSocialCreditCode",
                "source": "constructionSocialCreditCode",
                "type": "TEXT"
            },
            {
                "name": "constructionUnitName",
                "source": "constructionUnitName",
                "type": "TEXT"
            },
            {
                "name": "createTime",
                "source": "createTime",
                "type": "INTEGER"
            },
            {
                "name": "createrId",
                "source": "createrId",
                "type": "TEXT"
            },
            {
                "name": "currentConstructionStatus",
                "source": "currentConstructionStatus",
                "type": "TEXT"
            },
            {
                "name": "endTime",
                "source": "endTime",
                "type": "TEXT"
            },
            {
                "name": "excute",
                "source": "excute",
                "type": "TEXT"
            },
            {
                "name": "extra",
                "source": "extra",
                "type": "TEXT"
            },
            {
                "name": "id",
                "source": "id",
                "type": "TEXT"
            },
            {
                "name": "isAudit",
                "source": "isAudit",
                "type": "TEXT"
            },
            {
                "name": "isTop",
                "source": "isTop",
                "type": "TEXT"
            },
            {
                "name": "issueDate",
                "source": "issueDate",
                "type": "TEXT"
            },
            {
                "name": "mainRiskContent",
                "source": "mainRiskContent",
                "type": "TEXT"
            },
            {
                "name": "meetingCount",
                "source": "meetingCount",
                "type": "INTEGER"
            },
            {
                "name": "nextPerson",
                "source": "nextPerson",
                "type": "TEXT"
            },
            {
                "name": "pauseFlag",
                "source": "pauseFlag",
                "type": "TEXT"
            },
            {
                "name": "plannedEndDate",
                "source": "plannedEndDate",
                "type": "TEXT"
            },
            {
                "name": "plannedStartDate",
                "source": "plannedStartDate",
                "type": "TEXT"
            },
            {
                "name": "priority",
                "source": "priority",
                "type": "TEXT"
            },
            {
                "name": "provinceCode",
                "source": "provinceCode",
                "type": "TEXT"
            },
            {
                "name": "reAssessmentRiskLevel",
                "source": "reAssessmentRiskLevel",
                "type": "INTEGER"
            },
            {
                "name": "singleProjectCode",
                "source": "singleProjectCode",
                "type": "TEXT"
            },
            {
                "name": "singleProjectName",
                "source": "singleProjectName",
                "type": "TEXT"
            },
            {
                "name": "startTime",
                "source": "startTime",
                "type": "TEXT"
            },
            {
                "name": "subSectionProjectName",
                "source": "subSectionProjectName",
                "type": "TEXT"
            },
            {
                "name": "subcontractUnitName",
                "source": "subcontractUnitName",
                "type": "TEXT"
            },
            {
                "name": "supervisionSocialCreditCode",
                "source": "supervisionSocialCreditCode",
                "type": "TEXT"
            },
            {
                "name": "supervisionUnitName",
                "source": "supervisionUnitName",
                "type": "TEXT"
            },
            {
                "name": "teamId",
                "source": "teamId",
                "type": "TEXT"
            },
            {
                "name": "teamLeaderName",
                "source": "teamLeaderName",
                "type": "TEXT"
            },
            {
                "name": "teamSecurity",
                "source": "teamSecurity",
                "type": "TEXT"
            },
            {
                "name": "teamTechnology",
                "source": "teamTechnology",
                "type": "TEXT"
            },
            {
                "name": "ticketName",
                "source": "ticketName",
                "type": "TEXT"
            },
            {
                "name": "ticketNo",
                "source": "ticketNo",
                "type": "TEXT"
            },
            {
                "name": "ticketStatus",
                "source": "ticketStatus",
                "type": "TEXT"
            },
            {
                "name": "ticketType",
                "source": "ticketType",
                "type": "TEXT"
            },
            {
                "name": "traceId",
                "source": "traceId",
                "type": "TEXT"
            },
            {
                "name": "updateTime",
                "source": "updateTime",
                "type": "TEXT"
            },
            {
                "name": "workProcedure",
                "source": "workProcedure",
                "type": "TEXT"
            },
            {
                "name": "workSiteName",
                "source": "workSiteName",
                "type": "TEXT"
            },
            {
                "name": "workingTeamName",
                "source": "workingTeamName",
                "type": "TEXT"
            }
        ],
        "dataset_key": "dataset_b3dfb2d5",
        "key_candidates": [
            "id",
            "singleProjectCode",
            "biddingSectionCode",
            "singleProjectCode+biddingSectionCode"
        ],
        "page_name": "施工作业票",
        "parent_record_path": null,
        "partition_field": "singleProjectCode",
        "partition_key": "singleProjectCode",
        "plugin_id": "dcp-dataset-b3dfb2d5",
        "record_path": "raw_event",
        "record_type": "work_ticket:raw_event",
        "table": "canonical_p026_page_b3dfb2d5__work_ticket__raw_event"
    },
    {
        "api_name": "work_ticket",
        "api_path": "/apit/ebuild2-domain-security-work/v1/constrWorkTicket/queryConstrWorkTicketPagePc",
        "columns": [
            {
                "name": "extra",
                "source": "extra",
                "type": "TEXT"
            },
            {
                "name": "riskPrecautionId",
                "source": "riskPrecautionId",
                "type": "TEXT"
            },
            {
                "name": "subSectionProjectName",
                "source": "subSectionProjectName",
                "type": "TEXT"
            },
            {
                "name": "ticketId",
                "source": "ticketId",
                "type": "TEXT"
            },
            {
                "name": "traceId",
                "source": "traceId",
                "type": "TEXT"
            },
            {
                "name": "version",
                "source": "version",
                "type": "INTEGER"
            },
            {
                "name": "workProcedure",
                "source": "workProcedure",
                "type": "TEXT"
            },
            {
                "name": "workSiteName",
                "source": "workSiteName",
                "type": "TEXT"
            },
            {
                "name": "workType",
                "source": "workType",
                "type": "TEXT"
            },
            {
                "name": "workTypeText",
                "source": "workTypeText",
                "type": "TEXT"
            }
        ],
        "dataset_key": "dataset_b3dfb2d5",
        "key_candidates": [
            "ticketId"
        ],
        "page_name": "施工作业票",
        "parent_record_path": "raw_event",
        "partition_field": null,
        "partition_key": null,
        "plugin_id": "dcp-dataset-b3dfb2d5",
        "record_path": "raw_event.workTypeProcedureSiteNameDtos[]",
        "record_type": "work_ticket:raw_event.workTypeProcedureSiteNameDtos[]",
        "table": "canonical_p026_page_b3dfb2d5__work_ticket__raw_event_worktypeproceduresitenamedtos_items"
    },
    {
        "api_name": "work_ticket",
        "api_path": "/apit/ebuild2-domain-security-work/v1/constrWorkTicket/queryConstrWorkTicketPagePc",
        "columns": [
            {
                "name": "accessEndDate",
                "source": "accessEndDate",
                "type": "TEXT"
            },
            {
                "name": "accessState",
                "source": "accessState",
                "type": "TEXT"
            },
            {
                "name": "chosedFlag",
                "source": "chosedFlag",
                "type": "INTEGER"
            },
            {
                "name": "combinationId",
                "source": "combinationId",
                "type": "TEXT"
            },
            {
                "name": "companyName",
                "source": "companyName",
                "type": "TEXT"
            },
            {
                "name": "extra",
                "source": "extra",
                "type": "TEXT"
            },
            {
                "name": "id",
                "source": "id",
                "type": "TEXT"
            },
            {
                "name": "idCard",
                "source": "idCard",
                "type": "TEXT"
            },
            {
                "name": "idCardStr",
                "source": "idCardStr",
                "type": "TEXT"
            },
            {
                "name": "isGrey",
                "source": "isGrey",
                "type": "TEXT"
            },
            {
                "name": "isRed",
                "source": "isRed",
                "type": "TEXT"
            },
            {
                "name": "iscId",
                "source": "iscId",
                "type": "TEXT"
            },
            {
                "name": "mobile",
                "source": "mobile",
                "type": "TEXT"
            },
            {
                "name": "personnelId",
                "source": "personnelId",
                "type": "TEXT"
            },
            {
                "name": "positionCode",
                "source": "positionCode",
                "type": "TEXT"
            },
            {
                "name": "positionFlag",
                "source": "positionFlag",
                "type": "INTEGER"
            },
            {
                "name": "provOrgCode",
                "source": "provOrgCode",
                "type": "TEXT"
            },
            {
                "name": "provinceCode",
                "source": "provinceCode",
                "type": "TEXT"
            },
            {
                "name": "realName",
                "source": "realName",
                "type": "TEXT"
            },
            {
                "name": "redContent",
                "source": "redContent",
                "type": "TEXT"
            },
            {
                "name": "safetyPersonnelId",
                "source": "safetyPersonnelId",
                "type": "TEXT"
            },
            {
                "name": "ticketId",
                "source": "ticketId",
                "type": "TEXT"
            },
            {
                "name": "toolBoxTalkId",
                "source": "toolBoxTalkId",
                "type": "TEXT"
            },
            {
                "name": "traceId",
                "source": "traceId",
                "type": "TEXT"
            },
            {
                "name": "workCode",
                "source": "workCode",
                "type": "TEXT"
            },
            {
                "name": "workCodeText",
                "source": "workCodeText",
                "type": "TEXT"
            },
            {
                "name": "workDivision",
                "source": "workDivision",
                "type": "TEXT"
            }
        ],
        "dataset_key": "dataset_b3dfb2d5",
        "key_candidates": [
            "id",
            "ticketId"
        ],
        "page_name": "施工作业票",
        "parent_record_path": "raw_event",
        "partition_field": null,
        "partition_key": null,
        "plugin_id": "dcp-dataset-b3dfb2d5",
        "record_path": "raw_event.constrWorkTicketMemberSecurity[]",
        "record_type": "work_ticket:raw_event.constrWorkTicketMemberSecurity[]",
        "table": "canonical_p026_page_b3dfb2d5__work_ticket__raw_event_constrworkticketmembersecurity_items"
    },
    {
        "api_name": "countTicketNumPc",
        "api_path": "/apit/ebuild2-domain-security-work/v1/constrWorkTicket/countTicketNumPc",
        "columns": [
            {
                "name": "allNum",
                "source": "allNum",
                "type": "INTEGER"
            },
            {
                "name": "extra",
                "source": "extra",
                "type": "TEXT"
            },
            {
                "name": "reviewNum",
                "source": "reviewNum",
                "type": "INTEGER"
            },
            {
                "name": "reviewingNum",
                "source": "reviewingNum",
                "type": "INTEGER"
            },
            {
                "name": "traceId",
                "source": "traceId",
                "type": "TEXT"
            }
        ],
        "dataset_key": "dataset_b3dfb2d5",
        "key_candidates": [
            "source_record_key+record_path"
        ],
        "page_name": "施工作业票",
        "parent_record_path": null,
        "partition_field": null,
        "partition_key": null,
        "plugin_id": "dcp-dataset-b3dfb2d5",
        "record_path": "raw_event",
        "record_type": "countTicketNumPc:raw_event",
        "table": "canonical_p026_page_b3dfb2d5__countticketnumpc__raw_event"
    },
    {
        "api_name": "construction_tender_contract",
        "api_path": "/apit/ebuild2-domain-plan-foundation/v1/supervisorTenderingContract/getPageResult",
        "columns": [
            {
                "name": "bidTime",
                "source": "bidTime",
                "type": "TEXT"
            },
            {
                "name": "biddingPlanInteger",
                "source": "biddingPlanInteger",
                "type": "TEXT"
            },
            {
                "name": "bidpkgCode",
                "source": "bidpkgCode",
                "type": "TEXT"
            },
            {
                "name": "bidpkgName",
                "source": "bidpkgName",
                "type": "TEXT"
            },
            {
                "name": "buildUnitCode",
                "source": "buildUnitCode",
                "type": "TEXT"
            },
            {
                "name": "buildUnitName",
                "source": "buildUnitName",
                "type": "TEXT"
            },
            {
                "name": "companyCode",
                "source": "companyCode",
                "type": "TEXT"
            },
            {
                "name": "companyName",
                "source": "companyName",
                "type": "TEXT"
            },
            {
                "name": "contractAmount",
                "source": "contractAmount",
                "type": "TEXT"
            },
            {
                "name": "contractName",
                "source": "contractName",
                "type": "TEXT"
            },
            {
                "name": "contractNumber",
                "source": "contractNumber",
                "type": "TEXT"
            },
            {
                "name": "contractType",
                "source": "contractType",
                "type": "TEXT"
            },
            {
                "name": "id",
                "source": "id",
                "type": "TEXT"
            },
            {
                "name": "integrationFlag",
                "source": "integrationFlag",
                "type": "TEXT"
            },
            {
                "name": "operator",
                "source": "operator",
                "type": "TEXT"
            },
            {
                "name": "pageId",
                "source": "pageId",
                "type": "INTEGER"
            },
            {
                "name": "provinceCode",
                "source": "provinceCode",
                "type": "TEXT"
            },
            {
                "name": "provinceName",
                "source": "provinceName",
                "type": "TEXT"
            },
            {
                "name": "signTime",
                "source": "signTime",
                "type": "TEXT"
            },
            {
                "name": "status",
                "source": "status",
                "type": "TEXT"
            },
            {
                "name": "tenderingBatchName",
                "source": "tenderingBatchName",
                "type": "TEXT"
            },
            {
                "name": "userBuildUnitName",
                "source": "userBuildUnitName",
                "type": "TEXT"
            }
        ],
        "dataset_key": "dataset_2b1d6d14",
        "key_candidates": [
            "id"
        ],
        "page_name": "施工招投标及合同",
        "parent_record_path": null,
        "partition_field": null,
        "partition_key": null,
        "plugin_id": "dcp-dataset-2b1d6d14",
        "record_path": "raw_event",
        "record_type": "construction_tender_contract:raw_event",
        "table": "canonical_p027_page_2b1d6d14__construction_tender_contract__raw_event"
    },
    {
        "api_name": "queryConstructionDeptList",
        "api_path": "/apit/ebuild2-domain-project-form/v1/constructionPersonnelChange/queryConstructionDeptList",
        "columns": [
            {
                "name": "address",
                "source": "address",
                "type": "TEXT"
            },
            {
                "name": "affiliationCode",
                "source": "affiliationCode",
                "type": "TEXT"
            },
            {
                "name": "affiliationName",
                "source": "affiliationName",
                "type": "TEXT"
            },
            {
                "name": "bpmId",
                "source": "bpmId",
                "type": "TEXT"
            },
            {
                "name": "buildUnitCode",
                "source": "buildUnitCode",
                "type": "TEXT"
            },
            {
                "name": "contactTelephone",
                "source": "contactTelephone",
                "type": "TEXT"
            },
            {
                "name": "createTime",
                "source": "createTime",
                "type": "INTEGER"
            },
            {
                "name": "createrId",
                "source": "createrId",
                "type": "TEXT"
            },
            {
                "name": "deleteFlag",
                "source": "deleteFlag",
                "type": "INTEGER"
            },
            {
                "name": "departmentStatus",
                "source": "departmentStatus",
                "type": "INTEGER"
            },
            {
                "name": "departmentType",
                "source": "departmentType",
                "type": "INTEGER"
            },
            {
                "name": "deptCitiesCode",
                "source": "deptCitiesCode",
                "type": "INTEGER"
            },
            {
                "name": "deptCitiesName",
                "source": "deptCitiesName",
                "type": "TEXT"
            },
            {
                "name": "deptDistrictCode",
                "source": "deptDistrictCode",
                "type": "INTEGER"
            },
            {
                "name": "deptDistrictName",
                "source": "deptDistrictName",
                "type": "TEXT"
            },
            {
                "name": "deptId",
                "source": "deptId",
                "type": "TEXT"
            },
            {
                "name": "deptProvinceCode",
                "source": "deptProvinceCode",
                "type": "INTEGER"
            },
            {
                "name": "deptProvinceName",
                "source": "deptProvinceName",
                "type": "TEXT"
            },
            {
                "name": "emailAddress",
                "source": "emailAddress",
                "type": "TEXT"
            },
            {
                "name": "establishmentDate",
                "source": "establishmentDate",
                "type": "TEXT"
            },
            {
                "name": "extra",
                "source": "extra",
                "type": "TEXT"
            },
            {
                "name": "faxNo",
                "source": "faxNo",
                "type": "TEXT"
            },
            {
                "name": "groupMarkup",
                "source": "groupMarkup",
                "type": "TEXT"
            },
            {
                "name": "historyFlag",
                "source": "historyFlag",
                "type": "INTEGER"
            },
            {
                "name": "isHaveReset",
                "source": "isHaveReset",
                "type": "TEXT"
            },
            {
                "name": "personnelId",
                "source": "personnelId",
                "type": "TEXT"
            },
            {
                "name": "postalCode",
                "source": "postalCode",
                "type": "TEXT"
            },
            {
                "name": "prjManageMode",
                "source": "prjManageMode",
                "type": "TEXT"
            },
            {
                "name": "projectDepartmentName",
                "source": "projectDepartmentName",
                "type": "TEXT"
            },
            {
                "name": "projectDeptNo",
                "source": "projectDeptNo",
                "type": "TEXT"
            },
            {
                "name": "provinceCode",
                "source": "provinceCode",
                "type": "TEXT"
            },
            {
                "name": "realName",
                "source": "realName",
                "type": "TEXT"
            },
            {
                "name": "singnFlag",
                "source": "singnFlag",
                "type": "TEXT"
            },
            {
                "name": "traceId",
                "source": "traceId",
                "type": "TEXT"
            },
            {
                "name": "updateTime",
                "source": "updateTime",
                "type": "INTEGER"
            },
            {
                "name": "updaterId",
                "source": "updaterId",
                "type": "TEXT"
            },
            {
                "name": "year",
                "source": "year",
                "type": "TEXT"
            }
        ],
        "dataset_key": "dataset_f680e1a3",
        "key_candidates": [
            "source_record_key+record_path"
        ],
        "page_name": "施工资格报审",
        "parent_record_path": null,
        "partition_field": null,
        "partition_key": null,
        "plugin_id": "dcp-dataset-f680e1a3",
        "record_path": "raw_event",
        "record_type": "queryConstructionDeptList:raw_event",
        "table": "canonical_p028_page_f680e1a3__queryconstructiondeptlist__raw_event"
    },
    {
        "api_name": "page",
        "api_path": "/apit/ebuild2-domain-quality-accept/v1/divide/page",
        "columns": [
            {
                "name": "bidSectCode",
                "source": "bidSectCode",
                "type": "TEXT"
            },
            {
                "name": "bidSectName",
                "source": "bidSectName",
                "type": "TEXT"
            },
            {
                "name": "bpmId",
                "source": "bpmId",
                "type": "TEXT"
            },
            {
                "name": "bpmType",
                "source": "bpmType",
                "type": "INTEGER"
            },
            {
                "name": "compileDate",
                "source": "compileDate",
                "type": "TEXT"
            },
            {
                "name": "createProcessStatus",
                "source": "createProcessStatus",
                "type": "TEXT"
            },
            {
                "name": "divideName",
                "source": "divideName",
                "type": "TEXT"
            },
            {
                "name": "extra",
                "source": "extra",
                "type": "TEXT"
            },
            {
                "name": "fileId",
                "source": "fileId",
                "type": "TEXT"
            },
            {
                "name": "id",
                "source": "id",
                "type": "TEXT"
            },
            {
                "name": "instanceId",
                "source": "instanceId",
                "type": "TEXT"
            },
            {
                "name": "prjCode",
                "source": "prjCode",
                "type": "TEXT"
            },
            {
                "name": "prjName",
                "source": "prjName",
                "type": "TEXT"
            },
            {
                "name": "prjType",
                "source": "prjType",
                "type": "INTEGER"
            },
            {
                "name": "processStatus",
                "source": "processStatus",
                "type": "INTEGER"
            },
            {
                "name": "provinceCode",
                "source": "provinceCode",
                "type": "TEXT"
            },
            {
                "name": "resetFlag",
                "source": "resetFlag",
                "type": "INTEGER"
            },
            {
                "name": "sinPrjCode",
                "source": "sinPrjCode",
                "type": "TEXT"
            },
            {
                "name": "sinPrjName",
                "source": "sinPrjName",
                "type": "TEXT"
            },
            {
                "name": "templateName",
                "source": "templateName",
                "type": "TEXT"
            },
            {
                "name": "traceId",
                "source": "traceId",
                "type": "TEXT"
            },
            {
                "name": "uhvFlag",
                "source": "uhvFlag",
                "type": "TEXT"
            },
            {
                "name": "userId",
                "source": "userId",
                "type": "TEXT"
            },
            {
                "name": "userNode",
                "source": "userNode",
                "type": "TEXT"
            },
            {
                "name": "voltageLevel",
                "source": "voltageLevel",
                "type": "TEXT"
            },
            {
                "name": "wordTemplateId",
                "source": "wordTemplateId",
                "type": "TEXT"
            }
        ],
        "dataset_key": "dataset_f028b089",
        "key_candidates": [
            "id",
            "prjCode"
        ],
        "page_name": "施工过程验收",
        "parent_record_path": null,
        "partition_field": "prjCode",
        "partition_key": "prjCode",
        "plugin_id": "dcp-dataset-f028b089",
        "record_path": "raw_event",
        "record_type": "page:raw_event",
        "table": "canonical_p029_page_f028b089__page__raw_event"
    },
    {
        "api_name": "progInfo",
        "api_path": "/apit/ebuild2-domain-project-stage/v1/constrBoard/progInfo",
        "columns": [
            {
                "name": "approvalMessage",
                "source": "approvalMessage",
                "type": "TEXT"
            },
            {
                "name": "approvalStatus",
                "source": "approvalStatus",
                "type": "INTEGER"
            },
            {
                "name": "bidActualProgress",
                "source": "bidActualProgress",
                "type": "REAL"
            },
            {
                "name": "biddingSectionCode",
                "source": "biddingSectionCode",
                "type": "TEXT"
            },
            {
                "name": "biddingSectionName",
                "source": "biddingSectionName",
                "type": "TEXT"
            },
            {
                "name": "bpmId",
                "source": "bpmId",
                "type": "TEXT"
            },
            {
                "name": "planDuration",
                "source": "planDuration",
                "type": "INTEGER"
            },
            {
                "name": "plannedEndDate",
                "source": "plannedEndDate",
                "type": "TEXT"
            },
            {
                "name": "plannedStartDate",
                "source": "plannedStartDate",
                "type": "TEXT"
            },
            {
                "name": "prjActualProgress",
                "source": "prjActualProgress",
                "type": "REAL"
            },
            {
                "name": "rectifyProgress",
                "source": "rectifyProgress",
                "type": "TEXT"
            },
            {
                "name": "roleType",
                "source": "roleType",
                "type": "INTEGER"
            },
            {
                "name": "singleActualProgress",
                "source": "singleActualProgress",
                "type": "REAL"
            },
            {
                "name": "weightTemplate",
                "source": "weightTemplate",
                "type": "TEXT"
            }
        ],
        "dataset_key": "dataset_dfc0835a",
        "key_candidates": [
            "biddingSectionCode"
        ],
        "page_name": "施工进度看板",
        "parent_record_path": null,
        "partition_field": "biddingSectionCode",
        "partition_key": "biddingSectionCode",
        "plugin_id": "dcp-dataset-dfc0835a",
        "record_path": "raw_event",
        "record_type": "progInfo:raw_event",
        "table": "canonical_p030_page_dfc0835a__proginfo__raw_event"
    },
    {
        "api_name": "construction_progress_board_major_nodes",
        "api_path": "/apit/ebuild2-domain-project-stage/v1/constrBoard/progMajor",
        "columns": [
            {
                "name": "actualDuration",
                "source": "actualDuration",
                "type": "INTEGER"
            },
            {
                "name": "actualEndDate",
                "source": "actualEndDate",
                "type": "TEXT"
            },
            {
                "name": "actualProgress",
                "source": "actualProgress",
                "type": "REAL"
            },
            {
                "name": "actualStartDate",
                "source": "actualStartDate",
                "type": "TEXT"
            },
            {
                "name": "adjustFlag",
                "source": "adjustFlag",
                "type": "INTEGER"
            },
            {
                "name": "automaticProgress",
                "source": "automaticProgress",
                "type": "REAL"
            },
            {
                "name": "biddingSectionCode",
                "source": "biddingSectionCode",
                "type": "TEXT"
            },
            {
                "name": "configLevelArr",
                "source": "configLevelArr",
                "type": "TEXT"
            },
            {
                "name": "createTime",
                "source": "createTime",
                "type": "INTEGER"
            },
            {
                "name": "enterFlag",
                "source": "enterFlag",
                "type": "TEXT"
            },
            {
                "name": "extra",
                "source": "extra",
                "type": "TEXT"
            },
            {
                "name": "id",
                "source": "id",
                "type": "TEXT"
            },
            {
                "name": "majorName",
                "source": "majorName",
                "type": "TEXT"
            },
            {
                "name": "planDuration",
                "source": "planDuration",
                "type": "INTEGER"
            },
            {
                "name": "planProgress",
                "source": "planProgress",
                "type": "REAL"
            },
            {
                "name": "plannedEndDate",
                "source": "plannedEndDate",
                "type": "TEXT"
            },
            {
                "name": "plannedStartDate",
                "source": "plannedStartDate",
                "type": "TEXT"
            },
            {
                "name": "processyStatus",
                "source": "processyStatus",
                "type": "INTEGER"
            },
            {
                "name": "qualificationFlag",
                "source": "qualificationFlag",
                "type": "TEXT"
            },
            {
                "name": "singleProjectCode",
                "source": "singleProjectCode",
                "type": "TEXT"
            },
            {
                "name": "specialtyCode",
                "source": "specialtyCode",
                "type": "INTEGER"
            },
            {
                "name": "specialtyType",
                "source": "specialtyType",
                "type": "INTEGER"
            },
            {
                "name": "traceId",
                "source": "traceId",
                "type": "TEXT"
            },
            {
                "name": "updateTime",
                "source": "updateTime",
                "type": "TEXT"
            },
            {
                "name": "weight",
                "source": "weight",
                "type": "REAL"
            }
        ],
        "dataset_key": "dataset_dfc0835a",
        "key_candidates": [
            "id",
            "singleProjectCode",
            "biddingSectionCode",
            "singleProjectCode+biddingSectionCode"
        ],
        "page_name": "施工进度看板",
        "parent_record_path": null,
        "partition_field": "singleProjectCode",
        "partition_key": "singleProjectCode",
        "plugin_id": "dcp-dataset-dfc0835a",
        "record_path": "raw_event",
        "record_type": "construction_progress_board_major_nodes:raw_event",
        "table": "canonical_p030_page_dfc0835a__construction_progress_board_major_nodes__raw_event"
    },
    {
        "api_name": "construction_progress_board_major_nodes",
        "api_path": "/apit/ebuild2-domain-project-stage/v1/constrBoard/progMajor",
        "columns": [
            {
                "name": "acceptId",
                "source": "acceptId",
                "type": "TEXT"
            },
            {
                "name": "acceptanceStatus",
                "source": "acceptanceStatus",
                "type": "TEXT"
            },
            {
                "name": "actualDuration",
                "source": "actualDuration",
                "type": "INTEGER"
            },
            {
                "name": "actualEndDate",
                "source": "actualEndDate",
                "type": "TEXT"
            },
            {
                "name": "actualProgress",
                "source": "actualProgress",
                "type": "REAL"
            },
            {
                "name": "actualStartDate",
                "source": "actualStartDate",
                "type": "TEXT"
            },
            {
                "name": "adjustFlag",
                "source": "adjustFlag",
                "type": "INTEGER"
            },
            {
                "name": "automaticProgress",
                "source": "automaticProgress",
                "type": "REAL"
            },
            {
                "name": "biddingSectionCode",
                "source": "biddingSectionCode",
                "type": "TEXT"
            },
            {
                "name": "children",
                "source": "children",
                "type": "TEXT"
            },
            {
                "name": "constrNodeType",
                "source": "constrNodeType",
                "type": "INTEGER"
            },
            {
                "name": "count",
                "source": "count",
                "type": "INTEGER"
            },
            {
                "name": "createTime",
                "source": "createTime",
                "type": "TEXT"
            },
            {
                "name": "extra",
                "source": "extra",
                "type": "TEXT"
            },
            {
                "name": "fileId",
                "source": "fileId",
                "type": "TEXT"
            },
            {
                "name": "hierarchical",
                "source": "hierarchical",
                "type": "INTEGER"
            },
            {
                "name": "id",
                "source": "id",
                "type": "TEXT"
            },
            {
                "name": "involveFlag",
                "source": "involveFlag",
                "type": "TEXT"
            },
            {
                "name": "leaf",
                "source": "leaf",
                "type": "INTEGER"
            },
            {
                "name": "parentId",
                "source": "parentId",
                "type": "TEXT"
            },
            {
                "name": "planDuration",
                "source": "planDuration",
                "type": "INTEGER"
            },
            {
                "name": "planProgress",
                "source": "planProgress",
                "type": "REAL"
            },
            {
                "name": "plannedEndDate",
                "source": "plannedEndDate",
                "type": "TEXT"
            },
            {
                "name": "plannedStartDate",
                "source": "plannedStartDate",
                "type": "TEXT"
            },
            {
                "name": "prjCodeInspLot",
                "source": "prjCodeInspLot",
                "type": "TEXT"
            },
            {
                "name": "prjCodeSubSubentryPrj",
                "source": "prjCodeSubSubentryPrj",
                "type": "TEXT"
            },
            {
                "name": "prjCodeSubUnitPrj",
                "source": "prjCodeSubUnitPrj",
                "type": "TEXT"
            },
            {
                "name": "prjCodeSubentryPrj",
                "source": "prjCodeSubentryPrj",
                "type": "TEXT"
            },
            {
                "name": "prjCodeSubsecionPrj",
                "source": "prjCodeSubsecionPrj",
                "type": "TEXT"
            },
            {
                "name": "prjCodeUnitPrj",
                "source": "prjCodeUnitPrj",
                "type": "TEXT"
            },
            {
                "name": "procedureName",
                "source": "procedureName",
                "type": "TEXT"
            },
            {
                "name": "processyStatus",
                "source": "processyStatus",
                "type": "INTEGER"
            },
            {
                "name": "rectifyFlag",
                "source": "rectifyFlag",
                "type": "INTEGER"
            },
            {
                "name": "rectifyProgress",
                "source": "rectifyProgress",
                "type": "INTEGER"
            },
            {
                "name": "sectionLength",
                "source": "sectionLength",
                "type": "TEXT"
            },
            {
                "name": "serialNumber",
                "source": "serialNumber",
                "type": "INTEGER"
            },
            {
                "name": "serialQuery",
                "source": "serialQuery",
                "type": "TEXT"
            },
            {
                "name": "singleProjectCode",
                "source": "singleProjectCode",
                "type": "TEXT"
            },
            {
                "name": "siteType",
                "source": "siteType",
                "type": "TEXT"
            },
            {
                "name": "specialtyId",
                "source": "specialtyId",
                "type": "TEXT"
            },
            {
                "name": "standardNo",
                "source": "standardNo",
                "type": "TEXT"
            },
            {
                "name": "towerSectionId",
                "source": "towerSectionId",
                "type": "TEXT"
            },
            {
                "name": "towerSectionNo",
                "source": "towerSectionNo",
                "type": "TEXT"
            },
            {
                "name": "traceId",
                "source": "traceId",
                "type": "TEXT"
            },
            {
                "name": "updateTime",
                "source": "updateTime",
                "type": "TEXT"
            },
            {
                "name": "weight",
                "source": "weight",
                "type": "REAL"
            }
        ],
        "dataset_key": "dataset_dfc0835a",
        "key_candidates": [
            "id",
            "singleProjectCode",
            "biddingSectionCode",
            "singleProjectCode+biddingSectionCode"
        ],
        "page_name": "施工进度看板",
        "parent_record_path": "raw_event",
        "partition_field": "singleProjectCode",
        "partition_key": "singleProjectCode",
        "plugin_id": "dcp-dataset-dfc0835a",
        "record_path": "raw_event.constrNodeList[]",
        "record_type": "construction_progress_board_major_nodes:raw_event.constrNodeList[]",
        "table": "canonical_p030_page_dfc0835a__construction_progress_board_major_nodes__raw_event_constrnodelist_items"
    },
    {
        "api_name": "queryBaseInfo",
        "api_path": "/apit/ebuild2-domain-project-stage/v1/constrPlan/queryBaseInfo",
        "columns": [
            {
                "name": "applicaNum",
                "source": "applicaNum",
                "type": "TEXT"
            },
            {
                "name": "apprOpinions",
                "source": "apprOpinions",
                "type": "TEXT"
            },
            {
                "name": "apprTime",
                "source": "apprTime",
                "type": "TEXT"
            },
            {
                "name": "approvalStatus",
                "source": "approvalStatus",
                "type": "INTEGER"
            },
            {
                "name": "biddingSectionCode",
                "source": "biddingSectionCode",
                "type": "TEXT"
            },
            {
                "name": "biddingSectionName",
                "source": "biddingSectionName",
                "type": "TEXT"
            },
            {
                "name": "bpmId",
                "source": "bpmId",
                "type": "TEXT"
            },
            {
                "name": "currentDisposeId",
                "source": "currentDisposeId",
                "type": "TEXT"
            },
            {
                "name": "finishCheckFlag",
                "source": "finishCheckFlag",
                "type": "INTEGER"
            },
            {
                "name": "ownerDeptNo",
                "source": "ownerDeptNo",
                "type": "TEXT"
            },
            {
                "name": "ownerId",
                "source": "ownerId",
                "type": "TEXT"
            },
            {
                "name": "planDuration",
                "source": "planDuration",
                "type": "INTEGER"
            },
            {
                "name": "plannedEndDate",
                "source": "plannedEndDate",
                "type": "TEXT"
            },
            {
                "name": "plannedStartDate",
                "source": "plannedStartDate",
                "type": "TEXT"
            },
            {
                "name": "prjCode",
                "source": "prjCode",
                "type": "TEXT"
            },
            {
                "name": "professionalSupervisorDeptNo",
                "source": "professionalSupervisorDeptNo",
                "type": "TEXT"
            },
            {
                "name": "professionalSupervisorId",
                "source": "professionalSupervisorId",
                "type": "TEXT"
            },
            {
                "name": "renewal",
                "source": "renewal",
                "type": "INTEGER"
            },
            {
                "name": "roleType",
                "source": "roleType",
                "type": "INTEGER"
            },
            {
                "name": "signaturesStatus",
                "source": "signaturesStatus",
                "type": "INTEGER"
            },
            {
                "name": "supervisorDeptNo",
                "source": "supervisorDeptNo",
                "type": "TEXT"
            },
            {
                "name": "supervisorId",
                "source": "supervisorId",
                "type": "TEXT"
            },
            {
                "name": "type",
                "source": "type",
                "type": "INTEGER"
            },
            {
                "name": "upperLevelApprTime",
                "source": "upperLevelApprTime",
                "type": "TEXT"
            },
            {
                "name": "weightTemplate",
                "source": "weightTemplate",
                "type": "TEXT"
            }
        ],
        "dataset_key": "dataset_b419bad2",
        "key_candidates": [
            "prjCode",
            "biddingSectionCode",
            "prjCode+biddingSectionCode"
        ],
        "page_name": "施工进度计划",
        "parent_record_path": null,
        "partition_field": "prjCode",
        "partition_key": "prjCode",
        "plugin_id": "dcp-dataset-b419bad2",
        "record_path": "raw_event",
        "record_type": "queryBaseInfo:raw_event",
        "table": "canonical_p031_page_b419bad2__querybaseinfo__raw_event"
    },
    {
        "api_name": "construction_schedule_major_nodes",
        "api_path": "/apit/ebuild2-domain-project-stage/v1/constrPlan/queryMajorInfo",
        "columns": [
            {
                "name": "actualDuration",
                "source": "actualDuration",
                "type": "INTEGER"
            },
            {
                "name": "actualEndDate",
                "source": "actualEndDate",
                "type": "TEXT"
            },
            {
                "name": "actualProgress",
                "source": "actualProgress",
                "type": "REAL"
            },
            {
                "name": "actualStartDate",
                "source": "actualStartDate",
                "type": "TEXT"
            },
            {
                "name": "adjustFlag",
                "source": "adjustFlag",
                "type": "INTEGER"
            },
            {
                "name": "automaticProgress",
                "source": "automaticProgress",
                "type": "REAL"
            },
            {
                "name": "biddingSectionCode",
                "source": "biddingSectionCode",
                "type": "TEXT"
            },
            {
                "name": "configLevelArr",
                "source": "configLevelArr",
                "type": "TEXT"
            },
            {
                "name": "createTime",
                "source": "createTime",
                "type": "INTEGER"
            },
            {
                "name": "enterFlag",
                "source": "enterFlag",
                "type": "TEXT"
            },
            {
                "name": "extra",
                "source": "extra",
                "type": "TEXT"
            },
            {
                "name": "id",
                "source": "id",
                "type": "TEXT"
            },
            {
                "name": "majorName",
                "source": "majorName",
                "type": "TEXT"
            },
            {
                "name": "planDuration",
                "source": "planDuration",
                "type": "INTEGER"
            },
            {
                "name": "planProgress",
                "source": "planProgress",
                "type": "REAL"
            },
            {
                "name": "plannedEndDate",
                "source": "plannedEndDate",
                "type": "TEXT"
            },
            {
                "name": "plannedStartDate",
                "source": "plannedStartDate",
                "type": "TEXT"
            },
            {
                "name": "processyStatus",
                "source": "processyStatus",
                "type": "INTEGER"
            },
            {
                "name": "qualificationFlag",
                "source": "qualificationFlag",
                "type": "TEXT"
            },
            {
                "name": "singleProjectCode",
                "source": "singleProjectCode",
                "type": "TEXT"
            },
            {
                "name": "specialtyCode",
                "source": "specialtyCode",
                "type": "INTEGER"
            },
            {
                "name": "specialtyType",
                "source": "specialtyType",
                "type": "INTEGER"
            },
            {
                "name": "traceId",
                "source": "traceId",
                "type": "TEXT"
            },
            {
                "name": "updateTime",
                "source": "updateTime",
                "type": "TEXT"
            },
            {
                "name": "weight",
                "source": "weight",
                "type": "REAL"
            }
        ],
        "dataset_key": "dataset_b419bad2",
        "key_candidates": [
            "id",
            "singleProjectCode",
            "biddingSectionCode",
            "singleProjectCode+biddingSectionCode"
        ],
        "page_name": "施工进度计划",
        "parent_record_path": null,
        "partition_field": "singleProjectCode",
        "partition_key": "singleProjectCode",
        "plugin_id": "dcp-dataset-b419bad2",
        "record_path": "raw_event",
        "record_type": "construction_schedule_major_nodes:raw_event",
        "table": "canonical_p031_page_b419bad2__construction_schedule_major_nodes__raw_event"
    },
    {
        "api_name": "construction_schedule_major_nodes",
        "api_path": "/apit/ebuild2-domain-project-stage/v1/constrPlan/queryMajorInfo",
        "columns": [
            {
                "name": "acceptId",
                "source": "acceptId",
                "type": "TEXT"
            },
            {
                "name": "acceptanceStatus",
                "source": "acceptanceStatus",
                "type": "TEXT"
            },
            {
                "name": "actualDuration",
                "source": "actualDuration",
                "type": "INTEGER"
            },
            {
                "name": "actualEndDate",
                "source": "actualEndDate",
                "type": "TEXT"
            },
            {
                "name": "actualProgress",
                "source": "actualProgress",
                "type": "REAL"
            },
            {
                "name": "actualStartDate",
                "source": "actualStartDate",
                "type": "TEXT"
            },
            {
                "name": "adjustFlag",
                "source": "adjustFlag",
                "type": "INTEGER"
            },
            {
                "name": "automaticProgress",
                "source": "automaticProgress",
                "type": "REAL"
            },
            {
                "name": "biddingSectionCode",
                "source": "biddingSectionCode",
                "type": "TEXT"
            },
            {
                "name": "children",
                "source": "children",
                "type": "TEXT"
            },
            {
                "name": "constrNodeType",
                "source": "constrNodeType",
                "type": "INTEGER"
            },
            {
                "name": "count",
                "source": "count",
                "type": "INTEGER"
            },
            {
                "name": "createTime",
                "source": "createTime",
                "type": "TEXT"
            },
            {
                "name": "extra",
                "source": "extra",
                "type": "TEXT"
            },
            {
                "name": "fileId",
                "source": "fileId",
                "type": "TEXT"
            },
            {
                "name": "hierarchical",
                "source": "hierarchical",
                "type": "INTEGER"
            },
            {
                "name": "id",
                "source": "id",
                "type": "TEXT"
            },
            {
                "name": "involveFlag",
                "source": "involveFlag",
                "type": "TEXT"
            },
            {
                "name": "leaf",
                "source": "leaf",
                "type": "INTEGER"
            },
            {
                "name": "parentId",
                "source": "parentId",
                "type": "TEXT"
            },
            {
                "name": "planDuration",
                "source": "planDuration",
                "type": "INTEGER"
            },
            {
                "name": "planProgress",
                "source": "planProgress",
                "type": "REAL"
            },
            {
                "name": "plannedEndDate",
                "source": "plannedEndDate",
                "type": "TEXT"
            },
            {
                "name": "plannedStartDate",
                "source": "plannedStartDate",
                "type": "TEXT"
            },
            {
                "name": "prjCodeInspLot",
                "source": "prjCodeInspLot",
                "type": "TEXT"
            },
            {
                "name": "prjCodeSubSubentryPrj",
                "source": "prjCodeSubSubentryPrj",
                "type": "TEXT"
            },
            {
                "name": "prjCodeSubUnitPrj",
                "source": "prjCodeSubUnitPrj",
                "type": "TEXT"
            },
            {
                "name": "prjCodeSubentryPrj",
                "source": "prjCodeSubentryPrj",
                "type": "TEXT"
            },
            {
                "name": "prjCodeSubsecionPrj",
                "source": "prjCodeSubsecionPrj",
                "type": "TEXT"
            },
            {
                "name": "prjCodeUnitPrj",
                "source": "prjCodeUnitPrj",
                "type": "TEXT"
            },
            {
                "name": "procedureName",
                "source": "procedureName",
                "type": "TEXT"
            },
            {
                "name": "processyStatus",
                "source": "processyStatus",
                "type": "INTEGER"
            },
            {
                "name": "rectifyFlag",
                "source": "rectifyFlag",
                "type": "INTEGER"
            },
            {
                "name": "rectifyProgress",
                "source": "rectifyProgress",
                "type": "REAL"
            },
            {
                "name": "sectionLength",
                "source": "sectionLength",
                "type": "TEXT"
            },
            {
                "name": "serialNumber",
                "source": "serialNumber",
                "type": "INTEGER"
            },
            {
                "name": "serialQuery",
                "source": "serialQuery",
                "type": "TEXT"
            },
            {
                "name": "singleProjectCode",
                "source": "singleProjectCode",
                "type": "TEXT"
            },
            {
                "name": "siteType",
                "source": "siteType",
                "type": "TEXT"
            },
            {
                "name": "specialtyId",
                "source": "specialtyId",
                "type": "TEXT"
            },
            {
                "name": "standardNo",
                "source": "standardNo",
                "type": "TEXT"
            },
            {
                "name": "towerSectionId",
                "source": "towerSectionId",
                "type": "TEXT"
            },
            {
                "name": "towerSectionNo",
                "source": "towerSectionNo",
                "type": "TEXT"
            },
            {
                "name": "traceId",
                "source": "traceId",
                "type": "TEXT"
            },
            {
                "name": "updateTime",
                "source": "updateTime",
                "type": "TEXT"
            },
            {
                "name": "weight",
                "source": "weight",
                "type": "REAL"
            }
        ],
        "dataset_key": "dataset_b419bad2",
        "key_candidates": [
            "id",
            "singleProjectCode",
            "biddingSectionCode",
            "singleProjectCode+biddingSectionCode"
        ],
        "page_name": "施工进度计划",
        "parent_record_path": "raw_event",
        "partition_field": "singleProjectCode",
        "partition_key": "singleProjectCode",
        "plugin_id": "dcp-dataset-b419bad2",
        "record_path": "raw_event.constrNodeList[]",
        "record_type": "construction_schedule_major_nodes:raw_event.constrNodeList[]",
        "table": "canonical_p031_page_b419bad2__construction_schedule_major_nodes__raw_event_constrnodelist_items"
    },
    {
        "api_name": "adjust",
        "api_path": "/apit/ebuild2-domain-project-stage/v1/constrPlan/history/adjust",
        "columns": [
            {
                "name": "adjustFlag",
                "source": "adjustFlag",
                "type": "INTEGER"
            },
            {
                "name": "applicaNum",
                "source": "applicaNum",
                "type": "TEXT"
            },
            {
                "name": "approverId",
                "source": "approverId",
                "type": "TEXT"
            },
            {
                "name": "createTime",
                "source": "createTime",
                "type": "TEXT"
            },
            {
                "name": "createrId",
                "source": "createrId",
                "type": "TEXT"
            },
            {
                "name": "deleteFlag",
                "source": "deleteFlag",
                "type": "INTEGER"
            },
            {
                "name": "fileId",
                "source": "fileId",
                "type": "TEXT"
            },
            {
                "name": "id",
                "source": "id",
                "type": "TEXT"
            },
            {
                "name": "ofdFileId",
                "source": "ofdFileId",
                "type": "TEXT"
            },
            {
                "name": "ownerApprOpinion",
                "source": "ownerApprOpinion",
                "type": "TEXT"
            },
            {
                "name": "ownerApprTime",
                "source": "ownerApprTime",
                "type": "TEXT"
            },
            {
                "name": "pprovedTime",
                "source": "pprovedTime",
                "type": "TEXT"
            },
            {
                "name": "processId",
                "source": "processId",
                "type": "TEXT"
            },
            {
                "name": "readjustReportTime",
                "source": "readjustReportTime",
                "type": "TEXT"
            },
            {
                "name": "reportId",
                "source": "reportId",
                "type": "TEXT"
            },
            {
                "name": "sgApprTime",
                "source": "sgApprTime",
                "type": "TEXT"
            },
            {
                "name": "sinActualProgress",
                "source": "sinActualProgress",
                "type": "REAL"
            },
            {
                "name": "sinPlanProgress",
                "source": "sinPlanProgress",
                "type": "REAL"
            },
            {
                "name": "speciSupervisorApprOpinion",
                "source": "speciSupervisorApprOpinion",
                "type": "TEXT"
            },
            {
                "name": "speciSupervisorApprTime",
                "source": "speciSupervisorApprTime",
                "type": "TEXT"
            },
            {
                "name": "supervisorApprOpinion",
                "source": "supervisorApprOpinion",
                "type": "TEXT"
            },
            {
                "name": "supervisorApprTime",
                "source": "supervisorApprTime",
                "type": "TEXT"
            },
            {
                "name": "templateId",
                "source": "templateId",
                "type": "TEXT"
            },
            {
                "name": "updateTime",
                "source": "updateTime",
                "type": "TEXT"
            },
            {
                "name": "updaterId",
                "source": "updaterId",
                "type": "TEXT"
            },
            {
                "name": "yearMonth",
                "source": "yearMonth",
                "type": "TEXT"
            }
        ],
        "dataset_key": "dataset_b419bad2",
        "key_candidates": [
            "id"
        ],
        "page_name": "施工进度计划",
        "parent_record_path": null,
        "partition_field": null,
        "partition_key": null,
        "plugin_id": "dcp-dataset-b419bad2",
        "record_path": "raw_event",
        "record_type": "adjust:raw_event",
        "table": "canonical_p031_page_b419bad2__adjust__raw_event"
    },
    {
        "api_name": "construction_dept_list",
        "api_path": "/apit/ebuild2-domain-project-form/v1/constructionDept/queryConstructionDeptListAPP",
        "columns": [
            {
                "name": "address",
                "source": "address",
                "type": "TEXT"
            },
            {
                "name": "affiliationCode",
                "source": "affiliationCode",
                "type": "TEXT"
            },
            {
                "name": "affiliationName",
                "source": "affiliationName",
                "type": "TEXT"
            },
            {
                "name": "bpmId",
                "source": "bpmId",
                "type": "TEXT"
            },
            {
                "name": "buildUnitCode",
                "source": "buildUnitCode",
                "type": "TEXT"
            },
            {
                "name": "contactTelephone",
                "source": "contactTelephone",
                "type": "TEXT"
            },
            {
                "name": "createTime",
                "source": "createTime",
                "type": "INTEGER"
            },
            {
                "name": "createrId",
                "source": "createrId",
                "type": "TEXT"
            },
            {
                "name": "deleteFlag",
                "source": "deleteFlag",
                "type": "INTEGER"
            },
            {
                "name": "departmentStatus",
                "source": "departmentStatus",
                "type": "INTEGER"
            },
            {
                "name": "departmentType",
                "source": "departmentType",
                "type": "INTEGER"
            },
            {
                "name": "deptCitiesCode",
                "source": "deptCitiesCode",
                "type": "INTEGER"
            },
            {
                "name": "deptCitiesName",
                "source": "deptCitiesName",
                "type": "TEXT"
            },
            {
                "name": "deptDistrictCode",
                "source": "deptDistrictCode",
                "type": "INTEGER"
            },
            {
                "name": "deptDistrictName",
                "source": "deptDistrictName",
                "type": "TEXT"
            },
            {
                "name": "deptId",
                "source": "deptId",
                "type": "TEXT"
            },
            {
                "name": "deptProvinceCode",
                "source": "deptProvinceCode",
                "type": "INTEGER"
            },
            {
                "name": "deptProvinceName",
                "source": "deptProvinceName",
                "type": "TEXT"
            },
            {
                "name": "emailAddress",
                "source": "emailAddress",
                "type": "TEXT"
            },
            {
                "name": "establishmentDate",
                "source": "establishmentDate",
                "type": "TEXT"
            },
            {
                "name": "extra",
                "source": "extra",
                "type": "TEXT"
            },
            {
                "name": "faxNo",
                "source": "faxNo",
                "type": "TEXT"
            },
            {
                "name": "groupMarkup",
                "source": "groupMarkup",
                "type": "TEXT"
            },
            {
                "name": "historyFlag",
                "source": "historyFlag",
                "type": "INTEGER"
            },
            {
                "name": "isHaveReset",
                "source": "isHaveReset",
                "type": "TEXT"
            },
            {
                "name": "personnelId",
                "source": "personnelId",
                "type": "TEXT"
            },
            {
                "name": "postalCode",
                "source": "postalCode",
                "type": "TEXT"
            },
            {
                "name": "prjManageMode",
                "source": "prjManageMode",
                "type": "TEXT"
            },
            {
                "name": "projectDepartmentName",
                "source": "projectDepartmentName",
                "type": "TEXT"
            },
            {
                "name": "projectDeptNo",
                "source": "projectDeptNo",
                "type": "TEXT"
            },
            {
                "name": "provinceCode",
                "source": "provinceCode",
                "type": "TEXT"
            },
            {
                "name": "realName",
                "source": "realName",
                "type": "TEXT"
            },
            {
                "name": "singnFlag",
                "source": "singnFlag",
                "type": "TEXT"
            },
            {
                "name": "traceId",
                "source": "traceId",
                "type": "TEXT"
            },
            {
                "name": "updateTime",
                "source": "updateTime",
                "type": "INTEGER"
            },
            {
                "name": "updaterId",
                "source": "updaterId",
                "type": "TEXT"
            },
            {
                "name": "year",
                "source": "year",
                "type": "TEXT"
            }
        ],
        "dataset_key": "dataset_b0c41434",
        "key_candidates": [
            "source_record_key+record_path"
        ],
        "page_name": "施工项目部",
        "parent_record_path": null,
        "partition_field": null,
        "partition_key": null,
        "plugin_id": "dcp-dataset-b0c41434",
        "record_path": "raw_event",
        "record_type": "construction_dept_list:raw_event",
        "table": "canonical_p032_page_b0c41434__construction_dept_list__raw_event"
    },
    {
        "api_name": "construction_dept_personnel",
        "api_path": "/apit/ebuild2-domain-project-form/v1/constructionPerson/queryDeptPerson",
        "columns": [
            {
                "name": "beforeId",
                "source": "beforeId",
                "type": "TEXT"
            },
            {
                "name": "beforeName",
                "source": "beforeName",
                "type": "TEXT"
            },
            {
                "name": "buildername",
                "source": "buildername",
                "type": "TEXT"
            },
            {
                "name": "certificates",
                "source": "certificates",
                "type": "TEXT"
            },
            {
                "name": "changeFlag",
                "source": "changeFlag",
                "type": "TEXT"
            },
            {
                "name": "deleteFlag",
                "source": "deleteFlag",
                "type": "TEXT"
            },
            {
                "name": "deptKey",
                "source": "deptKey",
                "type": "INTEGER"
            },
            {
                "name": "dprId",
                "source": "dprId",
                "type": "TEXT"
            },
            {
                "name": "engineerRecordId",
                "source": "engineerRecordId",
                "type": "TEXT"
            },
            {
                "name": "entryDate",
                "source": "entryDate",
                "type": "TEXT"
            },
            {
                "name": "exitDate",
                "source": "exitDate",
                "type": "TEXT"
            },
            {
                "name": "extra",
                "source": "extra",
                "type": "TEXT"
            },
            {
                "name": "gender",
                "source": "gender",
                "type": "TEXT"
            },
            {
                "name": "id",
                "source": "id",
                "type": "TEXT"
            },
            {
                "name": "idCard",
                "source": "idCard",
                "type": "TEXT"
            },
            {
                "name": "jobCode",
                "source": "jobCode",
                "type": "TEXT"
            },
            {
                "name": "jobName",
                "source": "jobName",
                "type": "TEXT"
            },
            {
                "name": "mobile",
                "source": "mobile",
                "type": "TEXT"
            },
            {
                "name": "personnelCap",
                "source": "personnelCap",
                "type": "INTEGER"
            },
            {
                "name": "positionCode",
                "source": "positionCode",
                "type": "TEXT"
            },
            {
                "name": "positionName",
                "source": "positionName",
                "type": "TEXT"
            },
            {
                "name": "provinceCode",
                "source": "provinceCode",
                "type": "TEXT"
            },
            {
                "name": "realName",
                "source": "realName",
                "type": "TEXT"
            },
            {
                "name": "specialty",
                "source": "specialty",
                "type": "TEXT"
            },
            {
                "name": "statusState",
                "source": "statusState",
                "type": "INTEGER"
            },
            {
                "name": "traceId",
                "source": "traceId",
                "type": "TEXT"
            },
            {
                "name": "unitName",
                "source": "unitName",
                "type": "TEXT"
            },
            {
                "name": "withinFlag",
                "source": "withinFlag",
                "type": "TEXT"
            }
        ],
        "dataset_key": "dataset_b0c41434",
        "key_candidates": [
            "id"
        ],
        "page_name": "施工项目部",
        "parent_record_path": null,
        "partition_field": null,
        "partition_key": null,
        "plugin_id": "dcp-dataset-b0c41434",
        "record_path": "raw_event",
        "record_type": "construction_dept_personnel:raw_event",
        "table": "canonical_p032_page_b0c41434__construction_dept_personnel__raw_event"
    },
    {
        "api_name": "construction_dept_personnel",
        "api_path": "/apit/ebuild2-domain-project-form/v1/constructionPerson/queryDeptPerson",
        "columns": [
            {
                "name": "certId",
                "source": "certId",
                "type": "TEXT"
            },
            {
                "name": "certName",
                "source": "certName",
                "type": "TEXT"
            },
            {
                "name": "certNameText",
                "source": "certNameText",
                "type": "TEXT"
            },
            {
                "name": "certStatus",
                "source": "certStatus",
                "type": "INTEGER"
            },
            {
                "name": "certType",
                "source": "certType",
                "type": "TEXT"
            },
            {
                "name": "certTypeText",
                "source": "certTypeText",
                "type": "TEXT"
            },
            {
                "name": "createTime",
                "source": "createTime",
                "type": "TEXT"
            },
            {
                "name": "createrId",
                "source": "createrId",
                "type": "TEXT"
            },
            {
                "name": "deleteFlag",
                "source": "deleteFlag",
                "type": "TEXT"
            },
            {
                "name": "deptId",
                "source": "deptId",
                "type": "TEXT"
            },
            {
                "name": "extra",
                "source": "extra",
                "type": "TEXT"
            },
            {
                "name": "id",
                "source": "id",
                "type": "TEXT"
            },
            {
                "name": "jobCode",
                "source": "jobCode",
                "type": "TEXT"
            },
            {
                "name": "jobName",
                "source": "jobName",
                "type": "TEXT"
            },
            {
                "name": "personnelId",
                "source": "personnelId",
                "type": "TEXT"
            },
            {
                "name": "traceId",
                "source": "traceId",
                "type": "TEXT"
            },
            {
                "name": "updateTime",
                "source": "updateTime",
                "type": "TEXT"
            },
            {
                "name": "updaterId",
                "source": "updaterId",
                "type": "TEXT"
            },
            {
                "name": "validEndDate",
                "source": "validEndDate",
                "type": "TEXT"
            }
        ],
        "dataset_key": "dataset_b0c41434",
        "key_candidates": [
            "id"
        ],
        "page_name": "施工项目部",
        "parent_record_path": "raw_event",
        "partition_field": null,
        "partition_key": null,
        "plugin_id": "dcp-dataset-b0c41434",
        "record_path": "raw_event.certificates[]",
        "record_type": "construction_dept_personnel:raw_event.certificates[]",
        "table": "canonical_p032_page_b0c41434__construction_dept_personnel__raw_event_certificates_items"
    },
    {
        "api_name": "queryConstructionDeptFile",
        "api_path": "/apit/ebuild2-domain-project-form/v1/constructionDept/queryConstructionDeptFile",
        "columns": [
            {
                "name": "approvalNode",
                "source": "approvalNode",
                "type": "INTEGER"
            },
            {
                "name": "authorizationMatter",
                "source": "authorizationMatter",
                "type": "TEXT"
            },
            {
                "name": "certificateName",
                "source": "certificateName",
                "type": "TEXT"
            },
            {
                "name": "certificateNo",
                "source": "certificateNo",
                "type": "TEXT"
            },
            {
                "name": "deleteFlag",
                "source": "deleteFlag",
                "type": "INTEGER"
            },
            {
                "name": "documentClass",
                "source": "documentClass",
                "type": "INTEGER"
            },
            {
                "name": "extra",
                "source": "extra",
                "type": "TEXT"
            },
            {
                "name": "fileId",
                "source": "fileId",
                "type": "TEXT"
            },
            {
                "name": "fileName",
                "source": "fileName",
                "type": "TEXT"
            },
            {
                "name": "id",
                "source": "id",
                "type": "TEXT"
            },
            {
                "name": "instanceId",
                "source": "instanceId",
                "type": "TEXT"
            },
            {
                "name": "isHaveReset",
                "source": "isHaveReset",
                "type": "TEXT"
            },
            {
                "name": "personnelId",
                "source": "personnelId",
                "type": "TEXT"
            },
            {
                "name": "practiceQualification",
                "source": "practiceQualification",
                "type": "TEXT"
            },
            {
                "name": "prjCode",
                "source": "prjCode",
                "type": "TEXT"
            },
            {
                "name": "prjName",
                "source": "prjName",
                "type": "TEXT"
            },
            {
                "name": "projectDepartmentId",
                "source": "projectDepartmentId",
                "type": "TEXT"
            },
            {
                "name": "signTime",
                "source": "signTime",
                "type": "TEXT"
            },
            {
                "name": "signatureFlag",
                "source": "signatureFlag",
                "type": "INTEGER"
            },
            {
                "name": "signaturesStatus",
                "source": "signaturesStatus",
                "type": "INTEGER"
            },
            {
                "name": "singnFlag",
                "source": "singnFlag",
                "type": "INTEGER"
            },
            {
                "name": "traceId",
                "source": "traceId",
                "type": "TEXT"
            }
        ],
        "dataset_key": "dataset_b0c41434",
        "key_candidates": [
            "id",
            "prjCode"
        ],
        "page_name": "施工项目部",
        "parent_record_path": null,
        "partition_field": "prjCode",
        "partition_key": "prjCode",
        "plugin_id": "dcp-dataset-b0c41434",
        "record_path": "raw_event",
        "record_type": "queryConstructionDeptFile:raw_event",
        "table": "canonical_p032_page_b0c41434__queryconstructiondeptfile__raw_event"
    },
    {
        "api_name": "queryConstructionDeptProject",
        "api_path": "/apit/ebuild2-domain-project-form/v1/constructionProject/queryConstructionDeptProject",
        "columns": [
            {
                "name": "actualCommencementDate",
                "source": "actualCommencementDate",
                "type": "TEXT"
            },
            {
                "name": "constrTransformerCapacity",
                "source": "constrTransformerCapacity",
                "type": "REAL"
            },
            {
                "name": "constructionLineLength",
                "source": "constructionLineLength",
                "type": "TEXT"
            },
            {
                "name": "extra",
                "source": "extra",
                "type": "TEXT"
            },
            {
                "name": "isDeptManage",
                "source": "isDeptManage",
                "type": "TEXT"
            },
            {
                "name": "plannedCommencementDate",
                "source": "plannedCommencementDate",
                "type": "TEXT"
            },
            {
                "name": "plannedCommissioningDate",
                "source": "plannedCommissioningDate",
                "type": "TEXT"
            },
            {
                "name": "prjCode",
                "source": "prjCode",
                "type": "TEXT"
            },
            {
                "name": "prjName",
                "source": "prjName",
                "type": "TEXT"
            },
            {
                "name": "projectManagement",
                "source": "projectManagement",
                "type": "TEXT"
            },
            {
                "name": "sortNum",
                "source": "sortNum",
                "type": "TEXT"
            },
            {
                "name": "traceId",
                "source": "traceId",
                "type": "TEXT"
            },
            {
                "name": "voltageLevel",
                "source": "voltageLevel",
                "type": "TEXT"
            },
            {
                "name": "voltageLevelText",
                "source": "voltageLevelText",
                "type": "TEXT"
            }
        ],
        "dataset_key": "dataset_b0c41434",
        "key_candidates": [
            "prjCode"
        ],
        "page_name": "施工项目部",
        "parent_record_path": null,
        "partition_field": "prjCode",
        "partition_key": "prjCode",
        "plugin_id": "dcp-dataset-b0c41434",
        "record_path": "raw_event",
        "record_type": "queryConstructionDeptProject:raw_event",
        "table": "canonical_p032_page_b0c41434__queryconstructiondeptproject__raw_event"
    },
    {
        "api_name": "queryConstructionDeptProject",
        "api_path": "/apit/ebuild2-domain-project-form/v1/constructionProject/queryConstructionDeptProject",
        "columns": [
            {
                "name": "actualCommencementDate",
                "source": "actualCommencementDate",
                "type": "TEXT"
            },
            {
                "name": "buildUnitCode",
                "source": "buildUnitCode",
                "type": "TEXT"
            },
            {
                "name": "buildUnitName",
                "source": "buildUnitName",
                "type": "TEXT"
            },
            {
                "name": "constrNature",
                "source": "constrNature",
                "type": "INTEGER"
            },
            {
                "name": "constrNatureText",
                "source": "constrNatureText",
                "type": "TEXT"
            },
            {
                "name": "constrTransformerCapacity",
                "source": "constrTransformerCapacity",
                "type": "REAL"
            },
            {
                "name": "constructionLineLength",
                "source": "constructionLineLength",
                "type": "TEXT"
            },
            {
                "name": "contractId",
                "source": "contractId",
                "type": "TEXT"
            },
            {
                "name": "extra",
                "source": "extra",
                "type": "TEXT"
            },
            {
                "name": "personnelDTOS",
                "source": "personnelDTOS",
                "type": "TEXT"
            },
            {
                "name": "plannedCommencementDate",
                "source": "plannedCommencementDate",
                "type": "TEXT"
            },
            {
                "name": "plannedCommissioningDate",
                "source": "plannedCommissioningDate",
                "type": "TEXT"
            },
            {
                "name": "prjCode",
                "source": "prjCode",
                "type": "TEXT"
            },
            {
                "name": "prjName",
                "source": "prjName",
                "type": "TEXT"
            },
            {
                "name": "projectManagement",
                "source": "projectManagement",
                "type": "TEXT"
            },
            {
                "name": "provinceCode",
                "source": "provinceCode",
                "type": "TEXT"
            },
            {
                "name": "provinceName",
                "source": "provinceName",
                "type": "TEXT"
            },
            {
                "name": "singleProjectCode",
                "source": "singleProjectCode",
                "type": "TEXT"
            },
            {
                "name": "singleProjectName",
                "source": "singleProjectName",
                "type": "TEXT"
            },
            {
                "name": "sortNum",
                "source": "sortNum",
                "type": "TEXT"
            },
            {
                "name": "traceId",
                "source": "traceId",
                "type": "TEXT"
            },
            {
                "name": "voltageLevel",
                "source": "voltageLevel",
                "type": "TEXT"
            }
        ],
        "dataset_key": "dataset_b0c41434",
        "key_candidates": [
            "prjCode",
            "singleProjectCode",
            "prjCode+singleProjectCode"
        ],
        "page_name": "施工项目部",
        "parent_record_path": "raw_event",
        "partition_field": "prjCode",
        "partition_key": "prjCode",
        "plugin_id": "dcp-dataset-b0c41434",
        "record_path": "raw_event.sinPrjDTOS[]",
        "record_type": "queryConstructionDeptProject:raw_event.sinPrjDTOS[]",
        "table": "canonical_p032_page_b0c41434__queryconstructiondeptproject__raw_event_sinprjdtos_items"
    },
    {
        "api_name": "queryConstructionDeptProject",
        "api_path": "/apit/ebuild2-domain-project-form/v1/constructionProject/queryConstructionDeptProject",
        "columns": [
            {
                "name": "biddingSectionCode",
                "source": "biddingSectionCode",
                "type": "TEXT"
            },
            {
                "name": "biddingSectionName",
                "source": "biddingSectionName",
                "type": "TEXT"
            },
            {
                "name": "biddingSectionType",
                "source": "biddingSectionType",
                "type": "TEXT"
            },
            {
                "name": "buildUnitCode",
                "source": "buildUnitCode",
                "type": "TEXT"
            },
            {
                "name": "buildUnitName",
                "source": "buildUnitName",
                "type": "TEXT"
            },
            {
                "name": "constrTransformerCapacity",
                "source": "constrTransformerCapacity",
                "type": "REAL"
            },
            {
                "name": "constructionLineLength",
                "source": "constructionLineLength",
                "type": "TEXT"
            },
            {
                "name": "constructionStatus",
                "source": "constructionStatus",
                "type": "TEXT"
            },
            {
                "name": "contractId",
                "source": "contractId",
                "type": "TEXT"
            },
            {
                "name": "deleteFlag",
                "source": "deleteFlag",
                "type": "TEXT"
            },
            {
                "name": "extra",
                "source": "extra",
                "type": "TEXT"
            },
            {
                "name": "id",
                "source": "id",
                "type": "TEXT"
            },
            {
                "name": "personnelDTOS",
                "source": "personnelDTOS",
                "type": "TEXT"
            },
            {
                "name": "planFinDate",
                "source": "planFinDate",
                "type": "TEXT"
            },
            {
                "name": "planStartDate",
                "source": "planStartDate",
                "type": "TEXT"
            },
            {
                "name": "prjCode",
                "source": "prjCode",
                "type": "TEXT"
            },
            {
                "name": "prjName",
                "source": "prjName",
                "type": "TEXT"
            },
            {
                "name": "provinceCode",
                "source": "provinceCode",
                "type": "TEXT"
            },
            {
                "name": "provinceName",
                "source": "provinceName",
                "type": "TEXT"
            },
            {
                "name": "singleProjectCode",
                "source": "singleProjectCode",
                "type": "TEXT"
            },
            {
                "name": "singleProjectName",
                "source": "singleProjectName",
                "type": "TEXT"
            },
            {
                "name": "sortNum",
                "source": "sortNum",
                "type": "TEXT"
            },
            {
                "name": "status",
                "source": "status",
                "type": "TEXT"
            },
            {
                "name": "traceId",
                "source": "traceId",
                "type": "TEXT"
            }
        ],
        "dataset_key": "dataset_b0c41434",
        "key_candidates": [
            "id",
            "prjCode",
            "singleProjectCode",
            "biddingSectionCode",
            "prjCode+singleProjectCode+biddingSectionCode"
        ],
        "page_name": "施工项目部",
        "parent_record_path": "raw_event.sinPrjDTOS[]",
        "partition_field": "prjCode",
        "partition_key": "prjCode",
        "plugin_id": "dcp-dataset-b0c41434",
        "record_path": "raw_event.sinPrjDTOS[].bidSectDTOS[]",
        "record_type": "queryConstructionDeptProject:raw_event.sinPrjDTOS[].bidSectDTOS[]",
        "table": "canonical_p032_page_b0c41434__queryconstructiondeptproject__raw_event_sinprjdtos_items_bidsectdtos_items"
    },
    {
        "api_name": "countList",
        "api_path": "/apit/ebuild2-domain-security-work/v1/taskDaily/countList",
        "columns": [
            {
                "name": "applyNum",
                "source": "applyNum",
                "type": "INTEGER"
            },
            {
                "name": "approveNum",
                "source": "approveNum",
                "type": "INTEGER"
            },
            {
                "name": "totalNum",
                "source": "totalNum",
                "type": "INTEGER"
            }
        ],
        "dataset_key": "dataset_bba03ca4",
        "key_candidates": [
            "source_record_key+record_path"
        ],
        "page_name": "日计划",
        "parent_record_path": null,
        "partition_field": null,
        "partition_key": null,
        "plugin_id": "dcp-dataset-bba03ca4",
        "record_path": "raw_event",
        "record_type": "countList:raw_event",
        "table": "canonical_p033_page_bba03ca4__countlist__raw_event"
    },
    {
        "api_name": "monthly_blackout_plan",
        "api_path": "/apit/ebuild2-domain-plan-foundation/v1/monthBlackoutPlan/queryMonthBlackoutPage",
        "columns": [
            {
                "name": "auditStatus",
                "source": "auditStatus",
                "type": "INTEGER"
            },
            {
                "name": "blackoutName",
                "source": "blackoutName",
                "type": "TEXT"
            },
            {
                "name": "id",
                "source": "id",
                "type": "TEXT"
            },
            {
                "name": "planAdd",
                "source": "planAdd",
                "type": "INTEGER"
            },
            {
                "name": "planBefore",
                "source": "planBefore",
                "type": "INTEGER"
            },
            {
                "name": "planCancel",
                "source": "planCancel",
                "type": "INTEGER"
            },
            {
                "name": "planDelay",
                "source": "planDelay",
                "type": "INTEGER"
            },
            {
                "name": "planDelayToCurrentMonth",
                "source": "planDelayToCurrentMonth",
                "type": "INTEGER"
            },
            {
                "name": "planMonth",
                "source": "planMonth",
                "type": "INTEGER"
            },
            {
                "name": "planNormal",
                "source": "planNormal",
                "type": "INTEGER"
            },
            {
                "name": "planPrjCount",
                "source": "planPrjCount",
                "type": "INTEGER"
            },
            {
                "name": "planYear",
                "source": "planYear",
                "type": "TEXT"
            },
            {
                "name": "provinceCode",
                "source": "provinceCode",
                "type": "TEXT"
            },
            {
                "name": "provinceName",
                "source": "provinceName",
                "type": "TEXT"
            },
            {
                "name": "releaseFlag",
                "source": "releaseFlag",
                "type": "INTEGER"
            },
            {
                "name": "reportUserId",
                "source": "reportUserId",
                "type": "TEXT"
            },
            {
                "name": "reportUserName",
                "source": "reportUserName",
                "type": "TEXT"
            },
            {
                "name": "returnReason",
                "source": "returnReason",
                "type": "TEXT"
            },
            {
                "name": "submitTime",
                "source": "submitTime",
                "type": "TEXT"
            },
            {
                "name": "unusePam",
                "source": "unusePam",
                "type": "TEXT"
            },
            {
                "name": "weaveUserId",
                "source": "weaveUserId",
                "type": "TEXT"
            },
            {
                "name": "weaveUserName",
                "source": "weaveUserName",
                "type": "TEXT"
            }
        ],
        "dataset_key": "dataset_371fcd3d",
        "key_candidates": [
            "id"
        ],
        "page_name": "月度停电计划上报与查看",
        "parent_record_path": null,
        "partition_field": null,
        "partition_key": null,
        "plugin_id": "dcp-dataset-371fcd3d",
        "record_path": "raw_event",
        "record_type": "monthly_blackout_plan:raw_event",
        "table": "canonical_p035_page_371fcd3d__monthly_blackout_plan__raw_event"
    },
    {
        "api_name": "monthly_blackout_plan_details",
        "api_path": "/apit/ebuild2-domain-plan-foundation/v1/monthBlackoutPlan/queryMonthBlackoutDetails",
        "columns": [
            {
                "name": "blackoutCode",
                "source": "blackoutCode",
                "type": "TEXT"
            },
            {
                "name": "blackoutId",
                "source": "blackoutId",
                "type": "TEXT"
            },
            {
                "name": "blackoutPlanStatus",
                "source": "blackoutPlanStatus",
                "type": "INTEGER"
            },
            {
                "name": "blackoutPlanStatusName",
                "source": "blackoutPlanStatusName",
                "type": "TEXT"
            },
            {
                "name": "declarationConstrEndDate",
                "source": "declarationConstrEndDate",
                "type": "TEXT"
            },
            {
                "name": "declarationConstrStartDate",
                "source": "declarationConstrStartDate",
                "type": "TEXT"
            },
            {
                "name": "declarationDays",
                "source": "declarationDays",
                "type": "TEXT"
            },
            {
                "name": "equipmentName",
                "source": "equipmentName",
                "type": "TEXT"
            },
            {
                "name": "fileId",
                "source": "fileId",
                "type": "TEXT"
            },
            {
                "name": "id",
                "source": "id",
                "type": "TEXT"
            },
            {
                "name": "jobContent",
                "source": "jobContent",
                "type": "TEXT"
            },
            {
                "name": "jobContentFive",
                "source": "jobContentFive",
                "type": "TEXT"
            },
            {
                "name": "jobContentFour",
                "source": "jobContentFour",
                "type": "TEXT"
            },
            {
                "name": "jobContentOne",
                "source": "jobContentOne",
                "type": "TEXT"
            },
            {
                "name": "jobContentSeven",
                "source": "jobContentSeven",
                "type": "TEXT"
            },
            {
                "name": "jobContentSix",
                "source": "jobContentSix",
                "type": "TEXT"
            },
            {
                "name": "jobContentThree",
                "source": "jobContentThree",
                "type": "TEXT"
            },
            {
                "name": "jobContentTwo",
                "source": "jobContentTwo",
                "type": "TEXT"
            },
            {
                "name": "overhaulId",
                "source": "overhaulId",
                "type": "TEXT"
            },
            {
                "name": "planBlackoutEndDate",
                "source": "planBlackoutEndDate",
                "type": "TEXT"
            },
            {
                "name": "planBlackoutStartDate",
                "source": "planBlackoutStartDate",
                "type": "TEXT"
            },
            {
                "name": "planFlag",
                "source": "planFlag",
                "type": "INTEGER"
            },
            {
                "name": "planMonth",
                "source": "planMonth",
                "type": "INTEGER"
            },
            {
                "name": "planYear",
                "source": "planYear",
                "type": "TEXT"
            },
            {
                "name": "prjCode",
                "source": "prjCode",
                "type": "TEXT"
            },
            {
                "name": "prjName",
                "source": "prjName",
                "type": "TEXT"
            },
            {
                "name": "projectOperationPlanDate",
                "source": "projectOperationPlanDate",
                "type": "TEXT"
            },
            {
                "name": "provinceCode",
                "source": "provinceCode",
                "type": "TEXT"
            },
            {
                "name": "provinceName",
                "source": "provinceName",
                "type": "TEXT"
            },
            {
                "name": "singleProjectCode",
                "source": "singleProjectCode",
                "type": "TEXT"
            },
            {
                "name": "singleProjectName",
                "source": "singleProjectName",
                "type": "TEXT"
            },
            {
                "name": "unDeclaredReason",
                "source": "unDeclaredReason",
                "type": "TEXT"
            },
            {
                "name": "unExecutionReason",
                "source": "unExecutionReason",
                "type": "TEXT"
            },
            {
                "name": "unExecutionReasonName",
                "source": "unExecutionReasonName",
                "type": "TEXT"
            },
            {
                "name": "voltageLevel",
                "source": "voltageLevel",
                "type": "TEXT"
            }
        ],
        "dataset_key": "dataset_371fcd3d",
        "key_candidates": [
            "id",
            "prjCode",
            "singleProjectCode",
            "prjCode+singleProjectCode"
        ],
        "page_name": "月度停电计划上报与查看",
        "parent_record_path": null,
        "partition_field": "prjCode",
        "partition_key": "prjCode",
        "plugin_id": "dcp-dataset-371fcd3d",
        "record_path": "raw_event",
        "record_type": "monthly_blackout_plan_details:raw_event",
        "table": "canonical_p035_page_371fcd3d__monthly_blackout_plan_details__raw_event"
    },
    {
        "api_name": "detail",
        "api_path": "/apit/ebuild2-domain-project-stage/v1/tenderingService/detail",
        "columns": [
            {
                "name": "adjTotPrice",
                "source": "adjTotPrice",
                "type": "TEXT"
            },
            {
                "name": "bidpkgName",
                "source": "bidpkgName",
                "type": "TEXT"
            },
            {
                "name": "constrTransformerCapacity",
                "source": "constrTransformerCapacity",
                "type": "TEXT"
            },
            {
                "name": "constructionLineLength",
                "source": "constructionLineLength",
                "type": "TEXT"
            },
            {
                "name": "id",
                "source": "id",
                "type": "TEXT"
            },
            {
                "name": "openbidDate",
                "source": "openbidDate",
                "type": "TEXT"
            },
            {
                "name": "plannedCommencementDate",
                "source": "plannedCommencementDate",
                "type": "TEXT"
            },
            {
                "name": "plannedCommissioningDate",
                "source": "plannedCommissioningDate",
                "type": "TEXT"
            },
            {
                "name": "prjCode",
                "source": "prjCode",
                "type": "TEXT"
            },
            {
                "name": "prjName",
                "source": "prjName",
                "type": "TEXT"
            },
            {
                "name": "publishNoticePrdtDate",
                "source": "publishNoticePrdtDate",
                "type": "TEXT"
            },
            {
                "name": "subbidName",
                "source": "subbidName",
                "type": "TEXT"
            },
            {
                "name": "suppName",
                "source": "suppName",
                "type": "TEXT"
            },
            {
                "name": "suppType",
                "source": "suppType",
                "type": "TEXT"
            },
            {
                "name": "tenderingBatchName",
                "source": "tenderingBatchName",
                "type": "TEXT"
            },
            {
                "name": "unitName",
                "source": "unitName",
                "type": "TEXT"
            },
            {
                "name": "voltageLevel",
                "source": "voltageLevel",
                "type": "TEXT"
            }
        ],
        "dataset_key": "dataset_9002ea9c",
        "key_candidates": [
            "id",
            "prjCode"
        ],
        "page_name": "服务类招标情况统计",
        "parent_record_path": null,
        "partition_field": "prjCode",
        "partition_key": "prjCode",
        "plugin_id": "dcp-dataset-9002ea9c",
        "record_path": "raw_event",
        "record_type": "detail:raw_event",
        "table": "canonical_p036_page_9002ea9c__detail__raw_event"
    },
    {
        "api_name": "construction_tender_contract",
        "api_path": "/apit/ebuild2-domain-plan-foundation/v1/supervisorTenderingContract/getPageResult",
        "columns": [
            {
                "name": "bidTime",
                "source": "bidTime",
                "type": "TEXT"
            },
            {
                "name": "biddingPlanInteger",
                "source": "biddingPlanInteger",
                "type": "TEXT"
            },
            {
                "name": "bidpkgCode",
                "source": "bidpkgCode",
                "type": "TEXT"
            },
            {
                "name": "bidpkgName",
                "source": "bidpkgName",
                "type": "TEXT"
            },
            {
                "name": "buildUnitCode",
                "source": "buildUnitCode",
                "type": "TEXT"
            },
            {
                "name": "buildUnitName",
                "source": "buildUnitName",
                "type": "TEXT"
            },
            {
                "name": "companyCode",
                "source": "companyCode",
                "type": "TEXT"
            },
            {
                "name": "companyName",
                "source": "companyName",
                "type": "TEXT"
            },
            {
                "name": "contractAmount",
                "source": "contractAmount",
                "type": "TEXT"
            },
            {
                "name": "contractName",
                "source": "contractName",
                "type": "TEXT"
            },
            {
                "name": "contractNumber",
                "source": "contractNumber",
                "type": "TEXT"
            },
            {
                "name": "contractType",
                "source": "contractType",
                "type": "TEXT"
            },
            {
                "name": "id",
                "source": "id",
                "type": "TEXT"
            },
            {
                "name": "integrationFlag",
                "source": "integrationFlag",
                "type": "TEXT"
            },
            {
                "name": "operator",
                "source": "operator",
                "type": "TEXT"
            },
            {
                "name": "pageId",
                "source": "pageId",
                "type": "INTEGER"
            },
            {
                "name": "provinceCode",
                "source": "provinceCode",
                "type": "TEXT"
            },
            {
                "name": "provinceName",
                "source": "provinceName",
                "type": "TEXT"
            },
            {
                "name": "signTime",
                "source": "signTime",
                "type": "TEXT"
            },
            {
                "name": "status",
                "source": "status",
                "type": "TEXT"
            },
            {
                "name": "tenderingBatchName",
                "source": "tenderingBatchName",
                "type": "TEXT"
            },
            {
                "name": "userBuildUnitName",
                "source": "userBuildUnitName",
                "type": "TEXT"
            }
        ],
        "dataset_key": "dataset_9002ea9c",
        "key_candidates": [
            "id"
        ],
        "page_name": "服务类招标情况统计",
        "parent_record_path": null,
        "partition_field": null,
        "partition_key": null,
        "plugin_id": "dcp-dataset-9002ea9c",
        "record_path": "raw_event",
        "record_type": "construction_tender_contract:raw_event",
        "table": "canonical_p036_page_9002ea9c__construction_tender_contract__raw_event"
    },
    {
        "api_name": "getProjectListByContractId",
        "api_path": "/apit/ebuild2-domain-plan-foundation/v1/supervisorTenderingContract/getProjectListByContractId",
        "columns": [
            {
                "name": "bidSectNo",
                "source": "bidSectNo",
                "type": "TEXT"
            },
            {
                "name": "biddingSectionCode",
                "source": "biddingSectionCode",
                "type": "TEXT"
            },
            {
                "name": "biddingSectionName",
                "source": "biddingSectionName",
                "type": "TEXT"
            },
            {
                "name": "contractId",
                "source": "contractId",
                "type": "TEXT"
            },
            {
                "name": "id",
                "source": "id",
                "type": "TEXT"
            },
            {
                "name": "prjCode",
                "source": "prjCode",
                "type": "TEXT"
            },
            {
                "name": "prjManageMode",
                "source": "prjManageMode",
                "type": "INTEGER"
            },
            {
                "name": "prjName",
                "source": "prjName",
                "type": "TEXT"
            },
            {
                "name": "singleProjectCode",
                "source": "singleProjectCode",
                "type": "TEXT"
            },
            {
                "name": "singleProjectName",
                "source": "singleProjectName",
                "type": "TEXT"
            }
        ],
        "dataset_key": "dataset_9002ea9c",
        "key_candidates": [
            "id",
            "prjCode",
            "singleProjectCode",
            "biddingSectionCode",
            "prjCode+singleProjectCode+biddingSectionCode"
        ],
        "page_name": "服务类招标情况统计",
        "parent_record_path": null,
        "partition_field": "prjCode",
        "partition_key": "prjCode",
        "plugin_id": "dcp-dataset-9002ea9c",
        "record_path": "raw_event",
        "record_type": "getProjectListByContractId:raw_event",
        "table": "canonical_p036_page_9002ea9c__getprojectlistbycontractid__raw_event"
    },
    {
        "api_name": "tower_single_projects",
        "api_path": "/apit/ebuild2-common-project-digitization/tower/getSingleProject",
        "columns": [
            {
                "name": "positionCode",
                "source": "positionCode",
                "type": "TEXT"
            },
            {
                "name": "positionName",
                "source": "positionName",
                "type": "TEXT"
            },
            {
                "name": "sectList",
                "source": "sectList",
                "type": "TEXT"
            },
            {
                "name": "singleProjectCode",
                "source": "singleProjectCode",
                "type": "TEXT"
            },
            {
                "name": "singleProjectName",
                "source": "singleProjectName",
                "type": "TEXT"
            },
            {
                "name": "singleProjectType",
                "source": "singleProjectType",
                "type": "INTEGER"
            }
        ],
        "dataset_key": "dataset_f58e1b9b",
        "key_candidates": [
            "singleProjectCode"
        ],
        "page_name": "杆塔信息",
        "parent_record_path": null,
        "partition_field": "singleProjectCode",
        "partition_key": "singleProjectCode",
        "plugin_id": "dcp-dataset-f58e1b9b",
        "record_path": "raw_event",
        "record_type": "tower_single_projects:raw_event",
        "table": "canonical_p037_page_f58e1b9b__tower_single_projects__raw_event"
    },
    {
        "api_name": "getBidSectBySinCode",
        "api_path": "/apit/ebuild2-common-project-digitization/tower/getBidSectBySinCode",
        "columns": [
            {
                "name": "biddingSectionCode",
                "source": "biddingSectionCode",
                "type": "TEXT"
            },
            {
                "name": "biddingSectionName",
                "source": "biddingSectionName",
                "type": "TEXT"
            }
        ],
        "dataset_key": "dataset_f58e1b9b",
        "key_candidates": [
            "biddingSectionCode"
        ],
        "page_name": "杆塔信息",
        "parent_record_path": null,
        "partition_field": "biddingSectionCode",
        "partition_key": "biddingSectionCode",
        "plugin_id": "dcp-dataset-f58e1b9b",
        "record_path": "raw_event",
        "record_type": "getBidSectBySinCode:raw_event",
        "table": "canonical_p037_page_f58e1b9b__getbidsectbysincode__raw_event"
    },
    {
        "api_name": "tower_details",
        "api_path": "/apit/ebuild2-agg-cmm-service-center/tower/getTowerPageResult",
        "columns": [
            {
                "name": "biddingSectionCode",
                "source": "biddingSectionCode",
                "type": "TEXT"
            },
            {
                "name": "borrowedFlag",
                "source": "borrowedFlag",
                "type": "INTEGER"
            },
            {
                "name": "btCpBlBlhd",
                "source": "btCpBlBlhd",
                "type": "TEXT"
            },
            {
                "name": "btCpBlDwdx",
                "source": "btCpBlDwdx",
                "type": "TEXT"
            },
            {
                "name": "btCpBlNum",
                "source": "btCpBlNum",
                "type": "TEXT"
            },
            {
                "name": "btCpBlType",
                "source": "btCpBlType",
                "type": "TEXT"
            },
            {
                "name": "bthfNum",
                "source": "bthfNum",
                "type": "TEXT"
            },
            {
                "name": "btllNum",
                "source": "btllNum",
                "type": "TEXT"
            },
            {
                "name": "btsgNum",
                "source": "btsgNum",
                "type": "TEXT"
            },
            {
                "name": "buildCode",
                "source": "buildCode",
                "type": "TEXT"
            },
            {
                "name": "cdpzNum",
                "source": "cdpzNum",
                "type": "TEXT"
            },
            {
                "name": "cdqlNum",
                "source": "cdqlNum",
                "type": "TEXT"
            },
            {
                "name": "centerPileElevation",
                "source": "centerPileElevation",
                "type": "REAL"
            },
            {
                "name": "circuitQuantity",
                "source": "circuitQuantity",
                "type": "TEXT"
            },
            {
                "name": "constructionDeptId",
                "source": "constructionDeptId",
                "type": "TEXT"
            },
            {
                "name": "constructionSequenceNo",
                "source": "constructionSequenceNo",
                "type": "INTEGER"
            },
            {
                "name": "controlLevel",
                "source": "controlLevel",
                "type": "TEXT"
            },
            {
                "name": "county",
                "source": "county",
                "type": "TEXT"
            },
            {
                "name": "cover4gFlag",
                "source": "cover4gFlag",
                "type": "INTEGER"
            },
            {
                "name": "createTime",
                "source": "createTime",
                "type": "INTEGER"
            },
            {
                "name": "createrId",
                "source": "createrId",
                "type": "TEXT"
            },
            {
                "name": "deleteFlag",
                "source": "deleteFlag",
                "type": "INTEGER"
            },
            {
                "name": "designChangeNo",
                "source": "designChangeNo",
                "type": "TEXT"
            },
            {
                "name": "deviseDeptId",
                "source": "deviseDeptId",
                "type": "TEXT"
            },
            {
                "name": "deviseSequenceNo",
                "source": "deviseSequenceNo",
                "type": "INTEGER"
            },
            {
                "name": "dismantleFlag",
                "source": "dismantleFlag",
                "type": "INTEGER"
            },
            {
                "name": "dqjckwNum",
                "source": "dqjckwNum",
                "type": "TEXT"
            },
            {
                "name": "dqqtqzNum",
                "source": "dqqtqzNum",
                "type": "TEXT"
            },
            {
                "name": "eastCoordinate",
                "source": "eastCoordinate",
                "type": "TEXT"
            },
            {
                "name": "fgNum",
                "source": "fgNum",
                "type": "TEXT"
            },
            {
                "name": "fragileAreaType",
                "source": "fragileAreaType",
                "type": "TEXT"
            },
            {
                "name": "gcgsNum",
                "source": "gcgsNum",
                "type": "TEXT"
            },
            {
                "name": "generalDesignFlag",
                "source": "generalDesignFlag",
                "type": "TEXT"
            },
            {
                "name": "geology",
                "source": "geology",
                "type": "TEXT"
            },
            {
                "name": "groundThingName",
                "source": "groundThingName",
                "type": "TEXT"
            },
            {
                "name": "hpczNum",
                "source": "hpczNum",
                "type": "TEXT"
            },
            {
                "name": "hpdcclNum",
                "source": "hpdcclNum",
                "type": "TEXT"
            },
            {
                "name": "id",
                "source": "id",
                "type": "TEXT"
            },
            {
                "name": "jpscstczNum",
                "source": "jpscstczNum",
                "type": "TEXT"
            },
            {
                "name": "jpsjckwNum",
                "source": "jpsjckwNum",
                "type": "TEXT"
            },
            {
                "name": "ktfgNum",
                "source": "ktfgNum",
                "type": "TEXT"
            },
            {
                "name": "latitude",
                "source": "latitude",
                "type": "TEXT"
            },
            {
                "name": "latitudeEdit",
                "source": "latitudeEdit",
                "type": "TEXT"
            },
            {
                "name": "longitude",
                "source": "longitude",
                "type": "TEXT"
            },
            {
                "name": "longitudeEdit",
                "source": "longitudeEdit",
                "type": "TEXT"
            },
            {
                "name": "lscsNum",
                "source": "lscsNum",
                "type": "TEXT"
            },
            {
                "name": "lsldNum",
                "source": "lsldNum",
                "type": "TEXT"
            },
            {
                "name": "lspsNum",
                "source": "lspsNum",
                "type": "TEXT"
            },
            {
                "name": "lssgNum",
                "source": "lssgNum",
                "type": "TEXT"
            },
            {
                "name": "majorCrossingFlag",
                "source": "majorCrossingFlag",
                "type": "TEXT"
            },
            {
                "name": "moduleNo",
                "source": "moduleNo",
                "type": "TEXT"
            },
            {
                "name": "nominalHeight",
                "source": "nominalHeight",
                "type": "REAL"
            },
            {
                "name": "northCoordinate",
                "source": "northCoordinate",
                "type": "TEXT"
            },
            {
                "name": "ownerDeptId",
                "source": "ownerDeptId",
                "type": "TEXT"
            },
            {
                "name": "ownerSequenceNo",
                "source": "ownerSequenceNo",
                "type": "INTEGER"
            },
            {
                "name": "pdfhGbNum",
                "source": "pdfhGbNum",
                "type": "TEXT"
            },
            {
                "name": "pdfhZdNum",
                "source": "pdfhZdNum",
                "type": "TEXT"
            },
            {
                "name": "permanentOccupationNum",
                "source": "permanentOccupationNum",
                "type": "TEXT"
            },
            {
                "name": "provinceCode",
                "source": "provinceCode",
                "type": "TEXT"
            },
            {
                "name": "recommendNum",
                "source": "recommendNum",
                "type": "TEXT"
            },
            {
                "name": "remark",
                "source": "remark",
                "type": "TEXT"
            },
            {
                "name": "representativeSpan",
                "source": "representativeSpan",
                "type": "TEXT"
            },
            {
                "name": "rotationDegree",
                "source": "rotationDegree",
                "type": "TEXT"
            },
            {
                "name": "runTowerCode",
                "source": "runTowerCode",
                "type": "TEXT"
            },
            {
                "name": "rzlswdNum",
                "source": "rzlswdNum",
                "type": "TEXT"
            },
            {
                "name": "sectionAdjustNum",
                "source": "sectionAdjustNum",
                "type": "TEXT"
            },
            {
                "name": "sectionDividePointFlag",
                "source": "sectionDividePointFlag",
                "type": "INTEGER"
            },
            {
                "name": "sectionId",
                "source": "sectionId",
                "type": "TEXT"
            },
            {
                "name": "sensitiveAreaName",
                "source": "sensitiveAreaName",
                "type": "TEXT"
            },
            {
                "name": "sensitiveAreaType",
                "source": "sensitiveAreaType",
                "type": "TEXT"
            },
            {
                "name": "singleProjectCode",
                "source": "singleProjectCode",
                "type": "TEXT"
            },
            {
                "name": "slope",
                "source": "slope",
                "type": "TEXT"
            },
            {
                "name": "span",
                "source": "span",
                "type": "TEXT"
            },
            {
                "name": "stentFlag",
                "source": "stentFlag",
                "type": "INTEGER"
            },
            {
                "name": "strBorrowedFlag",
                "source": "strBorrowedFlag",
                "type": "TEXT"
            },
            {
                "name": "strCover4gFlag",
                "source": "strCover4gFlag",
                "type": "TEXT"
            },
            {
                "name": "strDismantleFlag",
                "source": "strDismantleFlag",
                "type": "TEXT"
            },
            {
                "name": "strStentFlag",
                "source": "strStentFlag",
                "type": "TEXT"
            },
            {
                "name": "strTensionTowerFlag",
                "source": "strTensionTowerFlag",
                "type": "TEXT"
            },
            {
                "name": "supervisionDeptId",
                "source": "supervisionDeptId",
                "type": "TEXT"
            },
            {
                "name": "supervisionSequenceNo",
                "source": "supervisionSequenceNo",
                "type": "INTEGER"
            },
            {
                "name": "surplusSoilNum",
                "source": "surplusSoilNum",
                "type": "TEXT"
            },
            {
                "name": "surplusSoilType",
                "source": "surplusSoilType",
                "type": "TEXT"
            },
            {
                "name": "tensionSectionLength",
                "source": "tensionSectionLength",
                "type": "TEXT"
            },
            {
                "name": "tensionTowerFlag",
                "source": "tensionTowerFlag",
                "type": "INTEGER"
            },
            {
                "name": "topography",
                "source": "topography",
                "type": "TEXT"
            },
            {
                "name": "towerCuircuitNumber",
                "source": "towerCuircuitNumber",
                "type": "TEXT"
            },
            {
                "name": "towerFullHeight",
                "source": "towerFullHeight",
                "type": "REAL"
            },
            {
                "name": "towerLegBaseformFirst",
                "source": "towerLegBaseformFirst",
                "type": "TEXT"
            },
            {
                "name": "towerLegBaseformFirstGroupSecond",
                "source": "towerLegBaseformFirstGroupSecond",
                "type": "TEXT"
            },
            {
                "name": "towerLegBaseformFirstGroupThird",
                "source": "towerLegBaseformFirstGroupThird",
                "type": "TEXT"
            },
            {
                "name": "towerLegBaseformFourth",
                "source": "towerLegBaseformFourth",
                "type": "TEXT"
            },
            {
                "name": "towerLegBaseformFourthGroupSecond",
                "source": "towerLegBaseformFourthGroupSecond",
                "type": "TEXT"
            },
            {
                "name": "towerLegBaseformFourthGroupThird",
                "source": "towerLegBaseformFourthGroupThird",
                "type": "TEXT"
            },
            {
                "name": "towerLegBaseformSecond",
                "source": "towerLegBaseformSecond",
                "type": "TEXT"
            },
            {
                "name": "towerLegBaseformSecondGroupSecond",
                "source": "towerLegBaseformSecondGroupSecond",
                "type": "TEXT"
            },
            {
                "name": "towerLegBaseformSecondGroupThird",
                "source": "towerLegBaseformSecondGroupThird",
                "type": "TEXT"
            },
            {
                "name": "towerLegBaseformThird",
                "source": "towerLegBaseformThird",
                "type": "TEXT"
            },
            {
                "name": "towerLegBaseformThirdGroupSecond",
                "source": "towerLegBaseformThirdGroupSecond",
                "type": "TEXT"
            },
            {
                "name": "towerLegBaseformThirdGroupThird",
                "source": "towerLegBaseformThirdGroupThird",
                "type": "TEXT"
            },
            {
                "name": "towerLegMaxDepthFirst",
                "source": "towerLegMaxDepthFirst",
                "type": "TEXT"
            },
            {
                "name": "towerLegMaxDepthFirstGroupSecond",
                "source": "towerLegMaxDepthFirstGroupSecond",
                "type": "TEXT"
            },
            {
                "name": "towerLegMaxDepthFirstGroupThird",
                "source": "towerLegMaxDepthFirstGroupThird",
                "type": "TEXT"
            },
            {
                "name": "towerLegMaxDepthFourth",
                "source": "towerLegMaxDepthFourth",
                "type": "TEXT"
            },
            {
                "name": "towerLegMaxDepthFourthGroupSecond",
                "source": "towerLegMaxDepthFourthGroupSecond",
                "type": "TEXT"
            },
            {
                "name": "towerLegMaxDepthFourthGroupThird",
                "source": "towerLegMaxDepthFourthGroupThird",
                "type": "TEXT"
            },
            {
                "name": "towerLegMaxDepthSecond",
                "source": "towerLegMaxDepthSecond",
                "type": "TEXT"
            },
            {
                "name": "towerLegMaxDepthSecondGroupSecond",
                "source": "towerLegMaxDepthSecondGroupSecond",
                "type": "TEXT"
            },
            {
                "name": "towerLegMaxDepthSecondGroupThird",
                "source": "towerLegMaxDepthSecondGroupThird",
                "type": "TEXT"
            },
            {
                "name": "towerLegMaxDepthThird",
                "source": "towerLegMaxDepthThird",
                "type": "TEXT"
            },
            {
                "name": "towerLegMaxDepthThirdGroupSecond",
                "source": "towerLegMaxDepthThirdGroupSecond",
                "type": "TEXT"
            },
            {
                "name": "towerLegMaxDepthThirdGroupThird",
                "source": "towerLegMaxDepthThirdGroupThird",
                "type": "TEXT"
            },
            {
                "name": "towerNo",
                "source": "towerNo",
                "type": "TEXT"
            },
            {
                "name": "towerSequenceNo",
                "source": "towerSequenceNo",
                "type": "INTEGER"
            },
            {
                "name": "towerStructure",
                "source": "towerStructure",
                "type": "TEXT"
            },
            {
                "name": "towerType",
                "source": "towerType",
                "type": "TEXT"
            },
            {
                "name": "towerTypeNo",
                "source": "towerTypeNo",
                "type": "TEXT"
            },
            {
                "name": "towerWeight",
                "source": "towerWeight",
                "type": "REAL"
            },
            {
                "name": "town",
                "source": "town",
                "type": "TEXT"
            },
            {
                "name": "uhvFlag",
                "source": "uhvFlag",
                "type": "TEXT"
            },
            {
                "name": "updateTime",
                "source": "updateTime",
                "type": "INTEGER"
            },
            {
                "name": "updateType",
                "source": "updateType",
                "type": "INTEGER"
            },
            {
                "name": "updaterId",
                "source": "updaterId",
                "type": "TEXT"
            },
            {
                "name": "upstreamTowerNo",
                "source": "upstreamTowerNo",
                "type": "TEXT"
            },
            {
                "name": "village",
                "source": "village",
                "type": "TEXT"
            },
            {
                "name": "yzlswdNum",
                "source": "yzlswdNum",
                "type": "TEXT"
            },
            {
                "name": "zcNum",
                "source": "zcNum",
                "type": "TEXT"
            },
            {
                "name": "zlNum",
                "source": "zlNum",
                "type": "TEXT"
            },
            {
                "name": "zlZcztWzcc",
                "source": "zlZcztWzcc",
                "type": "TEXT"
            },
            {
                "name": "zwgsNum",
                "source": "zwgsNum",
                "type": "TEXT"
            }
        ],
        "dataset_key": "dataset_f58e1b9b",
        "key_candidates": [
            "id",
            "singleProjectCode",
            "biddingSectionCode",
            "towerNo",
            "singleProjectCode+biddingSectionCode+towerNo"
        ],
        "page_name": "杆塔信息",
        "parent_record_path": null,
        "partition_field": "singleProjectCode",
        "partition_key": "singleProjectCode",
        "plugin_id": "dcp-dataset-f58e1b9b",
        "record_path": "raw_event",
        "record_type": "tower_details:raw_event",
        "table": "canonical_p037_page_f58e1b9b__tower_details__raw_event"
    },
    {
        "api_name": "queryToolBoxTalkStatus",
        "api_path": "/apit/ebuild2-domain-security-work/v1/toolBoxTalk/queryToolBoxTalkStatus",
        "columns": [
            {
                "name": "all",
                "source": "all",
                "type": "INTEGER"
            },
            {
                "name": "doing",
                "source": "doing",
                "type": "INTEGER"
            },
            {
                "name": "extra",
                "source": "extra",
                "type": "TEXT"
            },
            {
                "name": "over",
                "source": "over",
                "type": "INTEGER"
            },
            {
                "name": "pause",
                "source": "pause",
                "type": "INTEGER"
            },
            {
                "name": "traceId",
                "source": "traceId",
                "type": "TEXT"
            }
        ],
        "dataset_key": "dataset_135eb70d",
        "key_candidates": [
            "source_record_key+record_path"
        ],
        "page_name": "每日站班会",
        "parent_record_path": null,
        "partition_field": null,
        "partition_key": null,
        "plugin_id": "dcp-dataset-135eb70d",
        "record_path": "raw_event",
        "record_type": "queryToolBoxTalkStatus:raw_event",
        "table": "canonical_p038_page_135eb70d__querytoolboxtalkstatus__raw_event"
    },
    {
        "api_name": "getStatisticsPageResult",
        "api_path": "/apit/ebuild2-domain-plan-foundation/v1/materialTenderingInfo/getStatisticsPageResult",
        "columns": [
            {
                "name": "actualCommencementDate",
                "source": "actualCommencementDate",
                "type": "TEXT"
            },
            {
                "name": "actualCommissioningDate",
                "source": "actualCommissioningDate",
                "type": "TEXT"
            },
            {
                "name": "constrNature",
                "source": "constrNature",
                "type": "TEXT"
            },
            {
                "name": "constrNatureName",
                "source": "constrNatureName",
                "type": "TEXT"
            },
            {
                "name": "constrTransformerCapacity",
                "source": "constrTransformerCapacity",
                "type": "TEXT"
            },
            {
                "name": "constructionLineLength",
                "source": "constructionLineLength",
                "type": "TEXT"
            },
            {
                "name": "constructionStatus",
                "source": "constructionStatus",
                "type": "TEXT"
            },
            {
                "name": "id",
                "source": "id",
                "type": "TEXT"
            },
            {
                "name": "plannedCommencementDate",
                "source": "plannedCommencementDate",
                "type": "TEXT"
            },
            {
                "name": "plannedCommissioningDate",
                "source": "plannedCommissioningDate",
                "type": "TEXT"
            },
            {
                "name": "prjCode",
                "source": "prjCode",
                "type": "TEXT"
            },
            {
                "name": "prjName",
                "source": "prjName",
                "type": "TEXT"
            },
            {
                "name": "purchaseOrderNum",
                "source": "purchaseOrderNum",
                "type": "INTEGER"
            },
            {
                "name": "serialNumber",
                "source": "serialNumber",
                "type": "TEXT"
            },
            {
                "name": "tenderingBatchNum",
                "source": "tenderingBatchNum",
                "type": "INTEGER"
            },
            {
                "name": "vendorNum",
                "source": "vendorNum",
                "type": "INTEGER"
            },
            {
                "name": "voltageLevel",
                "source": "voltageLevel",
                "type": "TEXT"
            },
            {
                "name": "voltageLevelName",
                "source": "voltageLevelName",
                "type": "TEXT"
            }
        ],
        "dataset_key": "dataset_64d9153f",
        "key_candidates": [
            "id",
            "prjCode"
        ],
        "page_name": "物资类招标情况统计",
        "parent_record_path": null,
        "partition_field": "prjCode",
        "partition_key": "prjCode",
        "plugin_id": "dcp-dataset-64d9153f",
        "record_path": "raw_event",
        "record_type": "getStatisticsPageResult:raw_event",
        "table": "canonical_p039_page_64d9153f__getstatisticspageresult__raw_event"
    },
    {
        "api_name": "getMaterialTenderingInfoPageResult",
        "api_path": "/apit/ebuild2-domain-plan-foundation/v1/materialTenderingInfo/getMaterialTenderingInfoPageResult",
        "columns": [
            {
                "name": "bidTime",
                "source": "bidTime",
                "type": "TEXT"
            },
            {
                "name": "contractAmount",
                "source": "contractAmount",
                "type": "TEXT"
            },
            {
                "name": "contractDeliveryDate",
                "source": "contractDeliveryDate",
                "type": "TEXT"
            },
            {
                "name": "contractName",
                "source": "contractName",
                "type": "TEXT"
            },
            {
                "name": "contractNumber",
                "source": "contractNumber",
                "type": "TEXT"
            },
            {
                "name": "id",
                "source": "id",
                "type": "TEXT"
            },
            {
                "name": "materialCode",
                "source": "materialCode",
                "type": "TEXT"
            },
            {
                "name": "materialDescription",
                "source": "materialDescription",
                "type": "TEXT"
            },
            {
                "name": "measureUnit",
                "source": "measureUnit",
                "type": "TEXT"
            },
            {
                "name": "number",
                "source": "number",
                "type": "INTEGER"
            },
            {
                "name": "pageId",
                "source": "pageId",
                "type": "INTEGER"
            },
            {
                "name": "prjNumber",
                "source": "prjNumber",
                "type": "TEXT"
            },
            {
                "name": "purchaseOrderNumber",
                "source": "purchaseOrderNumber",
                "type": "TEXT"
            },
            {
                "name": "singleProjectCode",
                "source": "singleProjectCode",
                "type": "TEXT"
            },
            {
                "name": "singleProjectName",
                "source": "singleProjectName",
                "type": "TEXT"
            },
            {
                "name": "tenderingBatchName",
                "source": "tenderingBatchName",
                "type": "TEXT"
            },
            {
                "name": "tenderingBatchNumber",
                "source": "tenderingBatchNumber",
                "type": "TEXT"
            },
            {
                "name": "totalPrice",
                "source": "totalPrice",
                "type": "TEXT"
            },
            {
                "name": "vendorName",
                "source": "vendorName",
                "type": "TEXT"
            },
            {
                "name": "vendorUserName",
                "source": "vendorUserName",
                "type": "TEXT"
            },
            {
                "name": "vendorUserPhone",
                "source": "vendorUserPhone",
                "type": "TEXT"
            }
        ],
        "dataset_key": "dataset_64d9153f",
        "key_candidates": [
            "id",
            "singleProjectCode"
        ],
        "page_name": "物资类招标情况统计",
        "parent_record_path": null,
        "partition_field": "singleProjectCode",
        "partition_key": "singleProjectCode",
        "plugin_id": "dcp-dataset-64d9153f",
        "record_path": "raw_event",
        "record_type": "getMaterialTenderingInfoPageResult:raw_event",
        "table": "canonical_p039_page_64d9153f__getmaterialtenderinginfopageresult__raw_event"
    },
    {
        "api_name": "site_instruction_approval",
        "api_path": "/apit/ebuild2-domain-economy-manage/v1/instruction/queryInstructionApprovalPage",
        "columns": [
            {
                "name": "approvInspectionFlag",
                "source": "approvInspectionFlag",
                "type": "INTEGER"
            },
            {
                "name": "approvUserId",
                "source": "approvUserId",
                "type": "TEXT"
            },
            {
                "name": "approvalFormNumber",
                "source": "approvalFormNumber",
                "type": "TEXT"
            },
            {
                "name": "checkDate",
                "source": "checkDate",
                "type": "TEXT"
            },
            {
                "name": "createrId",
                "source": "createrId",
                "type": "TEXT"
            },
            {
                "name": "delFlag",
                "source": "delFlag",
                "type": "INTEGER"
            },
            {
                "name": "editInspectionFlag",
                "source": "editInspectionFlag",
                "type": "INTEGER"
            },
            {
                "name": "id",
                "source": "id",
                "type": "TEXT"
            },
            {
                "name": "initiateDate",
                "source": "initiateDate",
                "type": "TEXT"
            },
            {
                "name": "instructionAmount",
                "source": "instructionAmount",
                "type": "TEXT"
            },
            {
                "name": "instructionReason",
                "source": "instructionReason",
                "type": "INTEGER"
            },
            {
                "name": "instructionReasonName",
                "source": "instructionReasonName",
                "type": "TEXT"
            },
            {
                "name": "instructionType",
                "source": "instructionType",
                "type": "INTEGER"
            },
            {
                "name": "otherReasonText",
                "source": "otherReasonText",
                "type": "TEXT"
            },
            {
                "name": "realName",
                "source": "realName",
                "type": "TEXT"
            },
            {
                "name": "reviewStatus",
                "source": "reviewStatus",
                "type": "TEXT"
            },
            {
                "name": "signStatus",
                "source": "signStatus",
                "type": "TEXT"
            },
            {
                "name": "submitFlag",
                "source": "submitFlag",
                "type": "INTEGER"
            },
            {
                "name": "supervisionDeptName",
                "source": "supervisionDeptName",
                "type": "TEXT"
            },
            {
                "name": "supervisionPrjDeptId",
                "source": "supervisionPrjDeptId",
                "type": "TEXT"
            },
            {
                "name": "viewInspectionFlag",
                "source": "viewInspectionFlag",
                "type": "INTEGER"
            }
        ],
        "dataset_key": "dataset_36f2621e",
        "key_candidates": [
            "id"
        ],
        "page_name": "现场签证审批单",
        "parent_record_path": null,
        "partition_field": null,
        "partition_key": null,
        "plugin_id": "dcp-dataset-36f2621e",
        "record_path": "raw_event",
        "record_type": "site_instruction_approval:raw_event",
        "table": "canonical_p040_page_36f2621e__site_instruction_approval__raw_event"
    },
    {
        "api_name": "queryInstructionApprovalCount",
        "api_path": "/apit/ebuild2-domain-economy-manage/v1/instruction/queryInstructionApprovalCount",
        "columns": [
            {
                "name": "allNum",
                "source": "allNum",
                "type": "INTEGER"
            },
            {
                "name": "myProcessNum",
                "source": "myProcessNum",
                "type": "INTEGER"
            },
            {
                "name": "ownHandleCount",
                "source": "ownHandleCount",
                "type": "INTEGER"
            },
            {
                "name": "unitCode",
                "source": "unitCode",
                "type": "TEXT"
            }
        ],
        "dataset_key": "dataset_36f2621e",
        "key_candidates": [
            "source_record_key+record_path"
        ],
        "page_name": "现场签证审批单",
        "parent_record_path": null,
        "partition_field": null,
        "partition_key": null,
        "plugin_id": "dcp-dataset-36f2621e",
        "record_path": "raw_event",
        "record_type": "queryInstructionApprovalCount:raw_event",
        "table": "canonical_p040_page_36f2621e__queryinstructionapprovalcount__raw_event"
    },
    {
        "api_name": "working_team_dissolved",
        "api_path": "/apit/ebuild2-domain-security-work/v1/team/queryWorkingTeamPage",
        "columns": [
            {
                "name": "ball18",
                "source": "ball18",
                "type": "TEXT"
            },
            {
                "name": "ball20",
                "source": "ball20",
                "type": "TEXT"
            },
            {
                "name": "ballList",
                "source": "ballList",
                "type": "TEXT"
            },
            {
                "name": "biddingSectionCode",
                "source": "biddingSectionCode",
                "type": "TEXT"
            },
            {
                "name": "biddingSectionName",
                "source": "biddingSectionName",
                "type": "TEXT"
            },
            {
                "name": "buildFlag",
                "source": "buildFlag",
                "type": "TEXT"
            },
            {
                "name": "buildUnitCode",
                "source": "buildUnitCode",
                "type": "TEXT"
            },
            {
                "name": "changeRecord",
                "source": "changeRecord",
                "type": "TEXT"
            },
            {
                "name": "dayMeetId",
                "source": "dayMeetId",
                "type": "TEXT"
            },
            {
                "name": "extra",
                "source": "extra",
                "type": "TEXT"
            },
            {
                "name": "huvFlag",
                "source": "huvFlag",
                "type": "TEXT"
            },
            {
                "name": "id",
                "source": "id",
                "type": "TEXT"
            },
            {
                "name": "isDishand",
                "source": "isDishand",
                "type": "TEXT"
            },
            {
                "name": "isLeader",
                "source": "isLeader",
                "type": "TEXT"
            },
            {
                "name": "leader",
                "source": "leader",
                "type": "TEXT"
            },
            {
                "name": "leaderPhone",
                "source": "leaderPhone",
                "type": "TEXT"
            },
            {
                "name": "menberNum",
                "source": "menberNum",
                "type": "INTEGER"
            },
            {
                "name": "other",
                "source": "other",
                "type": "TEXT"
            },
            {
                "name": "provinceCode",
                "source": "provinceCode",
                "type": "TEXT"
            },
            {
                "name": "provinceName",
                "source": "provinceName",
                "type": "TEXT"
            },
            {
                "name": "singleProjectCode",
                "source": "singleProjectCode",
                "type": "TEXT"
            },
            {
                "name": "singleProjectName",
                "source": "singleProjectName",
                "type": "TEXT"
            },
            {
                "name": "subcontractUnitId",
                "source": "subcontractUnitId",
                "type": "TEXT"
            },
            {
                "name": "subcontractUnitIdList",
                "source": "subcontractUnitIdList",
                "type": "TEXT"
            },
            {
                "name": "subcontractUnitName",
                "source": "subcontractUnitName",
                "type": "TEXT"
            },
            {
                "name": "traceId",
                "source": "traceId",
                "type": "TEXT"
            },
            {
                "name": "weekFlag",
                "source": "weekFlag",
                "type": "INTEGER"
            },
            {
                "name": "workingTeamAttribute",
                "source": "workingTeamAttribute",
                "type": "TEXT"
            },
            {
                "name": "workingTeamName",
                "source": "workingTeamName",
                "type": "TEXT"
            },
            {
                "name": "workingTeamType",
                "source": "workingTeamType",
                "type": "TEXT"
            },
            {
                "name": "workingTeamTypeList",
                "source": "workingTeamTypeList",
                "type": "TEXT"
            },
            {
                "name": "workingTeamTypeNameList",
                "source": "workingTeamTypeNameList",
                "type": "TEXT"
            }
        ],
        "dataset_key": "dataset_5e6c0f3e",
        "key_candidates": [
            "id",
            "singleProjectCode",
            "biddingSectionCode",
            "singleProjectCode+biddingSectionCode"
        ],
        "page_name": "班组组建",
        "parent_record_path": null,
        "partition_field": "singleProjectCode",
        "partition_key": "singleProjectCode",
        "plugin_id": "dcp-dataset-5e6c0f3e",
        "record_path": "raw_event",
        "record_type": "working_team_dissolved:raw_event",
        "table": "canonical_p041_page_5e6c0f3e__working_team_dissolved__raw_event"
    },
    {
        "api_name": "working_team_dissolved",
        "api_path": "/apit/ebuild2-domain-security-work/v1/team/queryWorkingTeamPage",
        "columns": [
            {
                "name": "extra",
                "source": "extra",
                "type": "TEXT"
            },
            {
                "name": "name",
                "source": "name",
                "type": "TEXT"
            },
            {
                "name": "traceId",
                "source": "traceId",
                "type": "TEXT"
            }
        ],
        "dataset_key": "dataset_5e6c0f3e",
        "key_candidates": [
            "source_record_key+record_path"
        ],
        "page_name": "班组组建",
        "parent_record_path": "raw_event",
        "partition_field": null,
        "partition_key": null,
        "plugin_id": "dcp-dataset-5e6c0f3e",
        "record_path": "raw_event.safe[]",
        "record_type": "working_team_dissolved:raw_event.safe[]",
        "table": "canonical_p041_page_5e6c0f3e__working_team_dissolved__raw_event_safe_items"
    },
    {
        "api_name": "working_team_dissolved",
        "api_path": "/apit/ebuild2-domain-security-work/v1/team/queryWorkingTeamPage",
        "columns": [
            {
                "name": "extra",
                "source": "extra",
                "type": "TEXT"
            },
            {
                "name": "name",
                "source": "name",
                "type": "TEXT"
            },
            {
                "name": "traceId",
                "source": "traceId",
                "type": "TEXT"
            }
        ],
        "dataset_key": "dataset_5e6c0f3e",
        "key_candidates": [
            "source_record_key+record_path"
        ],
        "page_name": "班组组建",
        "parent_record_path": "raw_event",
        "partition_field": null,
        "partition_key": null,
        "plugin_id": "dcp-dataset-5e6c0f3e",
        "record_path": "raw_event.technology[]",
        "record_type": "working_team_dissolved:raw_event.technology[]",
        "table": "canonical_p041_page_5e6c0f3e__working_team_dissolved__raw_event_technology_items"
    },
    {
        "api_name": "working_team_dissolved",
        "api_path": "/apit/ebuild2-domain-security-work/v1/team/queryWorkingTeamPage",
        "columns": [
            {
                "name": "cameraId",
                "source": "cameraId",
                "type": "TEXT"
            },
            {
                "name": "cameraNo",
                "source": "cameraNo",
                "type": "TEXT"
            },
            {
                "name": "dayMeetId",
                "source": "dayMeetId",
                "type": "TEXT"
            },
            {
                "name": "extra",
                "source": "extra",
                "type": "TEXT"
            },
            {
                "name": "id",
                "source": "id",
                "type": "TEXT"
            },
            {
                "name": "isOpen",
                "source": "isOpen",
                "type": "TEXT"
            },
            {
                "name": "teamId",
                "source": "teamId",
                "type": "TEXT"
            },
            {
                "name": "traceId",
                "source": "traceId",
                "type": "TEXT"
            }
        ],
        "dataset_key": "dataset_5e6c0f3e",
        "key_candidates": [
            "id"
        ],
        "page_name": "班组组建",
        "parent_record_path": "raw_event",
        "partition_field": null,
        "partition_key": null,
        "plugin_id": "dcp-dataset-5e6c0f3e",
        "record_path": "raw_event.ball[]",
        "record_type": "working_team_dissolved:raw_event.ball[]",
        "table": "canonical_p041_page_5e6c0f3e__working_team_dissolved__raw_event_ball_items"
    },
    {
        "api_name": "working_team_dissolved",
        "api_path": "/apit/ebuild2-domain-security-work/v1/team/queryWorkingTeamPage",
        "columns": [
            {
                "name": "extra",
                "source": "extra",
                "type": "TEXT"
            },
            {
                "name": "id",
                "source": "id",
                "type": "TEXT"
            },
            {
                "name": "isEnter",
                "source": "isEnter",
                "type": "TEXT"
            },
            {
                "name": "isLeader",
                "source": "isLeader",
                "type": "TEXT"
            },
            {
                "name": "isMember",
                "source": "isMember",
                "type": "TEXT"
            },
            {
                "name": "legalRepr",
                "source": "legalRepr",
                "type": "TEXT"
            },
            {
                "name": "provOrgCode",
                "source": "provOrgCode",
                "type": "TEXT"
            },
            {
                "name": "provinceCode",
                "source": "provinceCode",
                "type": "TEXT"
            },
            {
                "name": "subcontractorType",
                "source": "subcontractorType",
                "type": "TEXT"
            },
            {
                "name": "traceId",
                "source": "traceId",
                "type": "TEXT"
            },
            {
                "name": "unifiedSocialCreditId",
                "source": "unifiedSocialCreditId",
                "type": "TEXT"
            },
            {
                "name": "unitCode",
                "source": "unitCode",
                "type": "TEXT"
            },
            {
                "name": "unitName",
                "source": "unitName",
                "type": "TEXT"
            },
            {
                "name": "validityPeriod",
                "source": "validityPeriod",
                "type": "TEXT"
            },
            {
                "name": "validityPeriodString",
                "source": "validityPeriodString",
                "type": "TEXT"
            }
        ],
        "dataset_key": "dataset_5e6c0f3e",
        "key_candidates": [
            "id"
        ],
        "page_name": "班组组建",
        "parent_record_path": "raw_event",
        "partition_field": null,
        "partition_key": null,
        "plugin_id": "dcp-dataset-5e6c0f3e",
        "record_path": "raw_event.unitList[]",
        "record_type": "working_team_dissolved:raw_event.unitList[]",
        "table": "canonical_p041_page_5e6c0f3e__working_team_dissolved__raw_event_unitlist_items"
    },
    {
        "api_name": "construction_tender_contract",
        "api_path": "/apit/ebuild2-domain-plan-foundation/v1/supervisorTenderingContract/getPageResult",
        "columns": [
            {
                "name": "bidTime",
                "source": "bidTime",
                "type": "TEXT"
            },
            {
                "name": "biddingPlanInteger",
                "source": "biddingPlanInteger",
                "type": "TEXT"
            },
            {
                "name": "bidpkgCode",
                "source": "bidpkgCode",
                "type": "TEXT"
            },
            {
                "name": "bidpkgName",
                "source": "bidpkgName",
                "type": "TEXT"
            },
            {
                "name": "buildUnitCode",
                "source": "buildUnitCode",
                "type": "TEXT"
            },
            {
                "name": "buildUnitName",
                "source": "buildUnitName",
                "type": "TEXT"
            },
            {
                "name": "companyCode",
                "source": "companyCode",
                "type": "TEXT"
            },
            {
                "name": "companyName",
                "source": "companyName",
                "type": "TEXT"
            },
            {
                "name": "contractAmount",
                "source": "contractAmount",
                "type": "TEXT"
            },
            {
                "name": "contractName",
                "source": "contractName",
                "type": "TEXT"
            },
            {
                "name": "contractNumber",
                "source": "contractNumber",
                "type": "TEXT"
            },
            {
                "name": "contractType",
                "source": "contractType",
                "type": "TEXT"
            },
            {
                "name": "id",
                "source": "id",
                "type": "TEXT"
            },
            {
                "name": "integrationFlag",
                "source": "integrationFlag",
                "type": "TEXT"
            },
            {
                "name": "operator",
                "source": "operator",
                "type": "TEXT"
            },
            {
                "name": "pageId",
                "source": "pageId",
                "type": "INTEGER"
            },
            {
                "name": "provinceCode",
                "source": "provinceCode",
                "type": "TEXT"
            },
            {
                "name": "provinceName",
                "source": "provinceName",
                "type": "TEXT"
            },
            {
                "name": "signTime",
                "source": "signTime",
                "type": "TEXT"
            },
            {
                "name": "status",
                "source": "status",
                "type": "TEXT"
            },
            {
                "name": "tenderingBatchName",
                "source": "tenderingBatchName",
                "type": "TEXT"
            },
            {
                "name": "userBuildUnitName",
                "source": "userBuildUnitName",
                "type": "TEXT"
            }
        ],
        "dataset_key": "dataset_627918af",
        "key_candidates": [
            "id"
        ],
        "page_name": "监理招投标及合同",
        "parent_record_path": null,
        "partition_field": null,
        "partition_key": null,
        "plugin_id": "dcp-dataset-627918af",
        "record_path": "raw_event",
        "record_type": "construction_tender_contract:raw_event",
        "table": "canonical_p042_page_627918af__construction_tender_contract__raw_event"
    },
    {
        "api_name": "supervision_outline",
        "api_path": "/apit/ebuild2-domain-project-stage/v1/supervisorScheme/querySupervisorSchemePage",
        "columns": [
            {
                "name": "approvalFinishTime",
                "source": "approvalFinishTime",
                "type": "TEXT"
            },
            {
                "name": "approvalStatus",
                "source": "approvalStatus",
                "type": "INTEGER"
            },
            {
                "name": "bpmId",
                "source": "bpmId",
                "type": "TEXT"
            },
            {
                "name": "canApprove",
                "source": "canApprove",
                "type": "INTEGER"
            },
            {
                "name": "canDelete",
                "source": "canDelete",
                "type": "INTEGER"
            },
            {
                "name": "canEdit",
                "source": "canEdit",
                "type": "INTEGER"
            },
            {
                "name": "extra",
                "source": "extra",
                "type": "TEXT"
            },
            {
                "name": "id",
                "source": "id",
                "type": "TEXT"
            },
            {
                "name": "instanceId",
                "source": "instanceId",
                "type": "TEXT"
            },
            {
                "name": "ownerApprOpinion",
                "source": "ownerApprOpinion",
                "type": "TEXT"
            },
            {
                "name": "reportTime",
                "source": "reportTime",
                "type": "TEXT"
            },
            {
                "name": "schemeName",
                "source": "schemeName",
                "type": "TEXT"
            },
            {
                "name": "schemeReportFileId",
                "source": "schemeReportFileId",
                "type": "TEXT"
            },
            {
                "name": "schemeReportFileName",
                "source": "schemeReportFileName",
                "type": "TEXT"
            },
            {
                "name": "schemeReportId",
                "source": "schemeReportId",
                "type": "TEXT"
            },
            {
                "name": "schemeReportNumber",
                "source": "schemeReportNumber",
                "type": "TEXT"
            },
            {
                "name": "schemeReportPrjName",
                "source": "schemeReportPrjName",
                "type": "TEXT"
            },
            {
                "name": "schemeReportTime",
                "source": "schemeReportTime",
                "type": "TEXT"
            },
            {
                "name": "schemeType",
                "source": "schemeType",
                "type": "INTEGER"
            },
            {
                "name": "signaturesStatus",
                "source": "signaturesStatus",
                "type": "INTEGER"
            },
            {
                "name": "supervisingEngineerApprOpinion",
                "source": "supervisingEngineerApprOpinion",
                "type": "TEXT"
            },
            {
                "name": "supervisingEngineerApprTime",
                "source": "supervisingEngineerApprTime",
                "type": "TEXT"
            },
            {
                "name": "supervisingEngineerId",
                "source": "supervisingEngineerId",
                "type": "TEXT"
            },
            {
                "name": "traceId",
                "source": "traceId",
                "type": "TEXT"
            }
        ],
        "dataset_key": "dataset_bdbab29b",
        "key_candidates": [
            "id"
        ],
        "page_name": "监理策划",
        "parent_record_path": null,
        "partition_field": null,
        "partition_key": null,
        "plugin_id": "dcp-dataset-bdbab29b",
        "record_path": "raw_event",
        "record_type": "supervision_outline:raw_event",
        "table": "canonical_p043_page_bdbab29b__supervision_outline__raw_event"
    },
    {
        "api_name": "supervision_outline",
        "api_path": "/apit/ebuild2-domain-project-stage/v1/supervisorScheme/querySupervisorSchemePage",
        "columns": [
            {
                "name": "bidSectCode",
                "source": "bidSectCode",
                "type": "TEXT"
            },
            {
                "name": "extra",
                "source": "extra",
                "type": "TEXT"
            },
            {
                "name": "prjCode",
                "source": "prjCode",
                "type": "TEXT"
            },
            {
                "name": "relaFlag",
                "source": "relaFlag",
                "type": "TEXT"
            },
            {
                "name": "sinPrjCode",
                "source": "sinPrjCode",
                "type": "TEXT"
            },
            {
                "name": "sinPrjName",
                "source": "sinPrjName",
                "type": "TEXT"
            },
            {
                "name": "traceId",
                "source": "traceId",
                "type": "TEXT"
            }
        ],
        "dataset_key": "dataset_bdbab29b",
        "key_candidates": [
            "prjCode"
        ],
        "page_name": "监理策划",
        "parent_record_path": "raw_event",
        "partition_field": "prjCode",
        "partition_key": "prjCode",
        "plugin_id": "dcp-dataset-bdbab29b",
        "record_path": "raw_event.sinPrjList[]",
        "record_type": "supervision_outline:raw_event.sinPrjList[]",
        "table": "canonical_p043_page_bdbab29b__supervision_outline__raw_event_sinprjlist_items"
    },
    {
        "api_name": "supervision_outline",
        "api_path": "/apit/ebuild2-domain-project-stage/v1/supervisorScheme/querySupervisorSchemePage",
        "columns": [
            {
                "name": "bidSectCode",
                "source": "bidSectCode",
                "type": "TEXT"
            },
            {
                "name": "bidSectName",
                "source": "bidSectName",
                "type": "TEXT"
            },
            {
                "name": "deptId",
                "source": "deptId",
                "type": "TEXT"
            },
            {
                "name": "deptName",
                "source": "deptName",
                "type": "TEXT"
            },
            {
                "name": "extra",
                "source": "extra",
                "type": "TEXT"
            },
            {
                "name": "relaFlag",
                "source": "relaFlag",
                "type": "TEXT"
            },
            {
                "name": "traceId",
                "source": "traceId",
                "type": "TEXT"
            }
        ],
        "dataset_key": "dataset_bdbab29b",
        "key_candidates": [
            "source_record_key+record_path"
        ],
        "page_name": "监理策划",
        "parent_record_path": "raw_event.sinPrjList[]",
        "partition_field": null,
        "partition_key": null,
        "plugin_id": "dcp-dataset-bdbab29b",
        "record_path": "raw_event.sinPrjList[].sinBidList[]",
        "record_type": "supervision_outline:raw_event.sinPrjList[].sinBidList[]",
        "table": "canonical_p043_page_bdbab29b__supervision_outline__raw_event_sinprjlist_items_sinbidlist_items"
    },
    {
        "api_name": "supervision_dept_list",
        "api_path": "/apit/ebuild2-domain-project-form/v1/supervisorDept/queryDeptListAPP",
        "columns": [
            {
                "name": "address",
                "source": "address",
                "type": "TEXT"
            },
            {
                "name": "affiliationCode",
                "source": "affiliationCode",
                "type": "TEXT"
            },
            {
                "name": "affiliationName",
                "source": "affiliationName",
                "type": "TEXT"
            },
            {
                "name": "bpmId",
                "source": "bpmId",
                "type": "TEXT"
            },
            {
                "name": "buildUnitCode",
                "source": "buildUnitCode",
                "type": "TEXT"
            },
            {
                "name": "contactTelephone",
                "source": "contactTelephone",
                "type": "TEXT"
            },
            {
                "name": "createTime",
                "source": "createTime",
                "type": "INTEGER"
            },
            {
                "name": "createrId",
                "source": "createrId",
                "type": "TEXT"
            },
            {
                "name": "deleteFlag",
                "source": "deleteFlag",
                "type": "INTEGER"
            },
            {
                "name": "departmentStatus",
                "source": "departmentStatus",
                "type": "INTEGER"
            },
            {
                "name": "departmentType",
                "source": "departmentType",
                "type": "INTEGER"
            },
            {
                "name": "deptCitiesCode",
                "source": "deptCitiesCode",
                "type": "INTEGER"
            },
            {
                "name": "deptCitiesName",
                "source": "deptCitiesName",
                "type": "TEXT"
            },
            {
                "name": "deptDistrictCode",
                "source": "deptDistrictCode",
                "type": "INTEGER"
            },
            {
                "name": "deptDistrictName",
                "source": "deptDistrictName",
                "type": "TEXT"
            },
            {
                "name": "deptId",
                "source": "deptId",
                "type": "TEXT"
            },
            {
                "name": "deptProvinceCode",
                "source": "deptProvinceCode",
                "type": "TEXT"
            },
            {
                "name": "deptProvinceName",
                "source": "deptProvinceName",
                "type": "TEXT"
            },
            {
                "name": "emailAddress",
                "source": "emailAddress",
                "type": "TEXT"
            },
            {
                "name": "establishmentDate",
                "source": "establishmentDate",
                "type": "TEXT"
            },
            {
                "name": "extra",
                "source": "extra",
                "type": "TEXT"
            },
            {
                "name": "faxNo",
                "source": "faxNo",
                "type": "TEXT"
            },
            {
                "name": "groupMarkup",
                "source": "groupMarkup",
                "type": "TEXT"
            },
            {
                "name": "historyFlag",
                "source": "historyFlag",
                "type": "INTEGER"
            },
            {
                "name": "isHaveReset",
                "source": "isHaveReset",
                "type": "TEXT"
            },
            {
                "name": "personnelId",
                "source": "personnelId",
                "type": "TEXT"
            },
            {
                "name": "postalCode",
                "source": "postalCode",
                "type": "TEXT"
            },
            {
                "name": "projectDepartmentName",
                "source": "projectDepartmentName",
                "type": "TEXT"
            },
            {
                "name": "projectDeptNo",
                "source": "projectDeptNo",
                "type": "TEXT"
            },
            {
                "name": "provinceCode",
                "source": "provinceCode",
                "type": "TEXT"
            },
            {
                "name": "realName",
                "source": "realName",
                "type": "TEXT"
            },
            {
                "name": "singnFlag",
                "source": "singnFlag",
                "type": "TEXT"
            },
            {
                "name": "traceId",
                "source": "traceId",
                "type": "TEXT"
            },
            {
                "name": "updateTime",
                "source": "updateTime",
                "type": "INTEGER"
            },
            {
                "name": "updaterId",
                "source": "updaterId",
                "type": "TEXT"
            },
            {
                "name": "year",
                "source": "year",
                "type": "TEXT"
            }
        ],
        "dataset_key": "dataset_0e8c85a2",
        "key_candidates": [
            "source_record_key+record_path"
        ],
        "page_name": "监理项目部",
        "parent_record_path": null,
        "partition_field": null,
        "partition_key": null,
        "plugin_id": "dcp-dataset-0e8c85a2",
        "record_path": "raw_event",
        "record_type": "supervision_dept_list:raw_event",
        "table": "canonical_p044_page_0e8c85a2__supervision_dept_list__raw_event"
    },
    {
        "api_name": "supervision_dept_personnel",
        "api_path": "/apit/ebuild2-domain-project-form/v1/supervisorPerson/querySupervisorDeptPerson",
        "columns": [
            {
                "name": "beforeId",
                "source": "beforeId",
                "type": "TEXT"
            },
            {
                "name": "beforeName",
                "source": "beforeName",
                "type": "TEXT"
            },
            {
                "name": "buildername",
                "source": "buildername",
                "type": "TEXT"
            },
            {
                "name": "certificates",
                "source": "certificates",
                "type": "TEXT"
            },
            {
                "name": "changeFlag",
                "source": "changeFlag",
                "type": "TEXT"
            },
            {
                "name": "deleteFlag",
                "source": "deleteFlag",
                "type": "TEXT"
            },
            {
                "name": "deptKey",
                "source": "deptKey",
                "type": "INTEGER"
            },
            {
                "name": "dprId",
                "source": "dprId",
                "type": "TEXT"
            },
            {
                "name": "engineerRecordId",
                "source": "engineerRecordId",
                "type": "TEXT"
            },
            {
                "name": "entryDate",
                "source": "entryDate",
                "type": "TEXT"
            },
            {
                "name": "exitDate",
                "source": "exitDate",
                "type": "TEXT"
            },
            {
                "name": "extra",
                "source": "extra",
                "type": "TEXT"
            },
            {
                "name": "gender",
                "source": "gender",
                "type": "TEXT"
            },
            {
                "name": "id",
                "source": "id",
                "type": "TEXT"
            },
            {
                "name": "idCard",
                "source": "idCard",
                "type": "TEXT"
            },
            {
                "name": "jobCode",
                "source": "jobCode",
                "type": "TEXT"
            },
            {
                "name": "jobName",
                "source": "jobName",
                "type": "TEXT"
            },
            {
                "name": "mobile",
                "source": "mobile",
                "type": "TEXT"
            },
            {
                "name": "personnelCap",
                "source": "personnelCap",
                "type": "INTEGER"
            },
            {
                "name": "positionCode",
                "source": "positionCode",
                "type": "TEXT"
            },
            {
                "name": "positionName",
                "source": "positionName",
                "type": "TEXT"
            },
            {
                "name": "provinceCode",
                "source": "provinceCode",
                "type": "TEXT"
            },
            {
                "name": "provinceCodeText",
                "source": "provinceCodeText",
                "type": "TEXT"
            },
            {
                "name": "realName",
                "source": "realName",
                "type": "TEXT"
            },
            {
                "name": "specialty",
                "source": "specialty",
                "type": "TEXT"
            },
            {
                "name": "statusState",
                "source": "statusState",
                "type": "INTEGER"
            },
            {
                "name": "traceId",
                "source": "traceId",
                "type": "TEXT"
            },
            {
                "name": "unitName",
                "source": "unitName",
                "type": "TEXT"
            },
            {
                "name": "withinFlag",
                "source": "withinFlag",
                "type": "TEXT"
            }
        ],
        "dataset_key": "dataset_0e8c85a2",
        "key_candidates": [
            "id"
        ],
        "page_name": "监理项目部",
        "parent_record_path": null,
        "partition_field": null,
        "partition_key": null,
        "plugin_id": "dcp-dataset-0e8c85a2",
        "record_path": "raw_event",
        "record_type": "supervision_dept_personnel:raw_event",
        "table": "canonical_p044_page_0e8c85a2__supervision_dept_personnel__raw_event"
    },
    {
        "api_name": "supervision_dept_personnel",
        "api_path": "/apit/ebuild2-domain-project-form/v1/supervisorPerson/querySupervisorDeptPerson",
        "columns": [
            {
                "name": "certId",
                "source": "certId",
                "type": "TEXT"
            },
            {
                "name": "certName",
                "source": "certName",
                "type": "TEXT"
            },
            {
                "name": "certNameText",
                "source": "certNameText",
                "type": "TEXT"
            },
            {
                "name": "certStatus",
                "source": "certStatus",
                "type": "INTEGER"
            },
            {
                "name": "certType",
                "source": "certType",
                "type": "TEXT"
            },
            {
                "name": "certTypeText",
                "source": "certTypeText",
                "type": "TEXT"
            },
            {
                "name": "createTime",
                "source": "createTime",
                "type": "TEXT"
            },
            {
                "name": "createrId",
                "source": "createrId",
                "type": "TEXT"
            },
            {
                "name": "deleteFlag",
                "source": "deleteFlag",
                "type": "TEXT"
            },
            {
                "name": "deptId",
                "source": "deptId",
                "type": "TEXT"
            },
            {
                "name": "extra",
                "source": "extra",
                "type": "TEXT"
            },
            {
                "name": "id",
                "source": "id",
                "type": "TEXT"
            },
            {
                "name": "jobCode",
                "source": "jobCode",
                "type": "TEXT"
            },
            {
                "name": "jobName",
                "source": "jobName",
                "type": "TEXT"
            },
            {
                "name": "personnelId",
                "source": "personnelId",
                "type": "TEXT"
            },
            {
                "name": "traceId",
                "source": "traceId",
                "type": "TEXT"
            },
            {
                "name": "updateTime",
                "source": "updateTime",
                "type": "TEXT"
            },
            {
                "name": "updaterId",
                "source": "updaterId",
                "type": "TEXT"
            },
            {
                "name": "validEndDate",
                "source": "validEndDate",
                "type": "TEXT"
            }
        ],
        "dataset_key": "dataset_0e8c85a2",
        "key_candidates": [
            "id"
        ],
        "page_name": "监理项目部",
        "parent_record_path": "raw_event",
        "partition_field": null,
        "partition_key": null,
        "plugin_id": "dcp-dataset-0e8c85a2",
        "record_path": "raw_event.certificates[]",
        "record_type": "supervision_dept_personnel:raw_event.certificates[]",
        "table": "canonical_p044_page_0e8c85a2__supervision_dept_personnel__raw_event_certificates_items"
    },
    {
        "api_name": "queryDeptFile",
        "api_path": "/apit/ebuild2-domain-project-form/v1/supervisorDept/queryDeptFile",
        "columns": [
            {
                "name": "approvalNode",
                "source": "approvalNode",
                "type": "INTEGER"
            },
            {
                "name": "authorizationMatter",
                "source": "authorizationMatter",
                "type": "TEXT"
            },
            {
                "name": "certificateName",
                "source": "certificateName",
                "type": "TEXT"
            },
            {
                "name": "certificateNo",
                "source": "certificateNo",
                "type": "TEXT"
            },
            {
                "name": "deleteFlag",
                "source": "deleteFlag",
                "type": "INTEGER"
            },
            {
                "name": "documentClass",
                "source": "documentClass",
                "type": "INTEGER"
            },
            {
                "name": "extra",
                "source": "extra",
                "type": "TEXT"
            },
            {
                "name": "fileId",
                "source": "fileId",
                "type": "TEXT"
            },
            {
                "name": "fileName",
                "source": "fileName",
                "type": "TEXT"
            },
            {
                "name": "id",
                "source": "id",
                "type": "TEXT"
            },
            {
                "name": "instanceId",
                "source": "instanceId",
                "type": "TEXT"
            },
            {
                "name": "isHaveReset",
                "source": "isHaveReset",
                "type": "TEXT"
            },
            {
                "name": "personnelId",
                "source": "personnelId",
                "type": "TEXT"
            },
            {
                "name": "practiceQualification",
                "source": "practiceQualification",
                "type": "TEXT"
            },
            {
                "name": "prjCode",
                "source": "prjCode",
                "type": "TEXT"
            },
            {
                "name": "prjName",
                "source": "prjName",
                "type": "TEXT"
            },
            {
                "name": "projectDepartmentId",
                "source": "projectDepartmentId",
                "type": "TEXT"
            },
            {
                "name": "signTime",
                "source": "signTime",
                "type": "TEXT"
            },
            {
                "name": "signatureFlag",
                "source": "signatureFlag",
                "type": "INTEGER"
            },
            {
                "name": "signaturesStatus",
                "source": "signaturesStatus",
                "type": "INTEGER"
            },
            {
                "name": "singnFlag",
                "source": "singnFlag",
                "type": "INTEGER"
            },
            {
                "name": "traceId",
                "source": "traceId",
                "type": "TEXT"
            }
        ],
        "dataset_key": "dataset_0e8c85a2",
        "key_candidates": [
            "id",
            "prjCode"
        ],
        "page_name": "监理项目部",
        "parent_record_path": null,
        "partition_field": "prjCode",
        "partition_key": "prjCode",
        "plugin_id": "dcp-dataset-0e8c85a2",
        "record_path": "raw_event",
        "record_type": "queryDeptFile:raw_event",
        "table": "canonical_p044_page_0e8c85a2__querydeptfile__raw_event"
    },
    {
        "api_name": "querySupervisorDeptProject",
        "api_path": "/apit/ebuild2-domain-project-form/v1/supervisorProject/querySupervisorDeptProject",
        "columns": [
            {
                "name": "actualCommencementDate",
                "source": "actualCommencementDate",
                "type": "TEXT"
            },
            {
                "name": "constrTransformerCapacity",
                "source": "constrTransformerCapacity",
                "type": "REAL"
            },
            {
                "name": "constructionLineLength",
                "source": "constructionLineLength",
                "type": "TEXT"
            },
            {
                "name": "extra",
                "source": "extra",
                "type": "TEXT"
            },
            {
                "name": "isDeptManage",
                "source": "isDeptManage",
                "type": "TEXT"
            },
            {
                "name": "plannedCommencementDate",
                "source": "plannedCommencementDate",
                "type": "TEXT"
            },
            {
                "name": "plannedCommissioningDate",
                "source": "plannedCommissioningDate",
                "type": "TEXT"
            },
            {
                "name": "prjCode",
                "source": "prjCode",
                "type": "TEXT"
            },
            {
                "name": "prjName",
                "source": "prjName",
                "type": "TEXT"
            },
            {
                "name": "projectManagement",
                "source": "projectManagement",
                "type": "TEXT"
            },
            {
                "name": "sortNum",
                "source": "sortNum",
                "type": "TEXT"
            },
            {
                "name": "traceId",
                "source": "traceId",
                "type": "TEXT"
            },
            {
                "name": "voltageLevel",
                "source": "voltageLevel",
                "type": "TEXT"
            },
            {
                "name": "voltageLevelText",
                "source": "voltageLevelText",
                "type": "TEXT"
            }
        ],
        "dataset_key": "dataset_0e8c85a2",
        "key_candidates": [
            "prjCode"
        ],
        "page_name": "监理项目部",
        "parent_record_path": null,
        "partition_field": "prjCode",
        "partition_key": "prjCode",
        "plugin_id": "dcp-dataset-0e8c85a2",
        "record_path": "raw_event",
        "record_type": "querySupervisorDeptProject:raw_event",
        "table": "canonical_p044_page_0e8c85a2__querysupervisordeptproject__raw_event"
    },
    {
        "api_name": "querySupervisorDeptProject",
        "api_path": "/apit/ebuild2-domain-project-form/v1/supervisorProject/querySupervisorDeptProject",
        "columns": [
            {
                "name": "actualCommencementDate",
                "source": "actualCommencementDate",
                "type": "TEXT"
            },
            {
                "name": "buildUnitCode",
                "source": "buildUnitCode",
                "type": "TEXT"
            },
            {
                "name": "buildUnitName",
                "source": "buildUnitName",
                "type": "TEXT"
            },
            {
                "name": "constrNature",
                "source": "constrNature",
                "type": "INTEGER"
            },
            {
                "name": "constrNatureText",
                "source": "constrNatureText",
                "type": "TEXT"
            },
            {
                "name": "constrTransformerCapacity",
                "source": "constrTransformerCapacity",
                "type": "REAL"
            },
            {
                "name": "constructionLineLength",
                "source": "constructionLineLength",
                "type": "TEXT"
            },
            {
                "name": "contractId",
                "source": "contractId",
                "type": "TEXT"
            },
            {
                "name": "extra",
                "source": "extra",
                "type": "TEXT"
            },
            {
                "name": "personnelDTOS",
                "source": "personnelDTOS",
                "type": "TEXT"
            },
            {
                "name": "plannedCommencementDate",
                "source": "plannedCommencementDate",
                "type": "TEXT"
            },
            {
                "name": "plannedCommissioningDate",
                "source": "plannedCommissioningDate",
                "type": "TEXT"
            },
            {
                "name": "prjCode",
                "source": "prjCode",
                "type": "TEXT"
            },
            {
                "name": "prjName",
                "source": "prjName",
                "type": "TEXT"
            },
            {
                "name": "projectManagement",
                "source": "projectManagement",
                "type": "TEXT"
            },
            {
                "name": "provinceCode",
                "source": "provinceCode",
                "type": "TEXT"
            },
            {
                "name": "provinceName",
                "source": "provinceName",
                "type": "TEXT"
            },
            {
                "name": "singleProjectCode",
                "source": "singleProjectCode",
                "type": "TEXT"
            },
            {
                "name": "singleProjectName",
                "source": "singleProjectName",
                "type": "TEXT"
            },
            {
                "name": "singleProjectType",
                "source": "singleProjectType",
                "type": "TEXT"
            },
            {
                "name": "sortNum",
                "source": "sortNum",
                "type": "TEXT"
            },
            {
                "name": "traceId",
                "source": "traceId",
                "type": "TEXT"
            },
            {
                "name": "voltageLevel",
                "source": "voltageLevel",
                "type": "TEXT"
            }
        ],
        "dataset_key": "dataset_0e8c85a2",
        "key_candidates": [
            "prjCode",
            "singleProjectCode",
            "prjCode+singleProjectCode"
        ],
        "page_name": "监理项目部",
        "parent_record_path": "raw_event",
        "partition_field": "prjCode",
        "partition_key": "prjCode",
        "plugin_id": "dcp-dataset-0e8c85a2",
        "record_path": "raw_event.sinPrjDTOS[]",
        "record_type": "querySupervisorDeptProject:raw_event.sinPrjDTOS[]",
        "table": "canonical_p044_page_0e8c85a2__querysupervisordeptproject__raw_event_sinprjdtos_items"
    },
    {
        "api_name": "querySupervisorDeptProject",
        "api_path": "/apit/ebuild2-domain-project-form/v1/supervisorProject/querySupervisorDeptProject",
        "columns": [
            {
                "name": "biddingSectionCode",
                "source": "biddingSectionCode",
                "type": "TEXT"
            },
            {
                "name": "biddingSectionName",
                "source": "biddingSectionName",
                "type": "TEXT"
            },
            {
                "name": "biddingSectionType",
                "source": "biddingSectionType",
                "type": "TEXT"
            },
            {
                "name": "buildUnitCode",
                "source": "buildUnitCode",
                "type": "TEXT"
            },
            {
                "name": "buildUnitName",
                "source": "buildUnitName",
                "type": "TEXT"
            },
            {
                "name": "constrTransformerCapacity",
                "source": "constrTransformerCapacity",
                "type": "REAL"
            },
            {
                "name": "constructionLineLength",
                "source": "constructionLineLength",
                "type": "TEXT"
            },
            {
                "name": "constructionStatus",
                "source": "constructionStatus",
                "type": "TEXT"
            },
            {
                "name": "contractId",
                "source": "contractId",
                "type": "TEXT"
            },
            {
                "name": "deleteFlag",
                "source": "deleteFlag",
                "type": "TEXT"
            },
            {
                "name": "extra",
                "source": "extra",
                "type": "TEXT"
            },
            {
                "name": "id",
                "source": "id",
                "type": "TEXT"
            },
            {
                "name": "personnelDTOS",
                "source": "personnelDTOS",
                "type": "TEXT"
            },
            {
                "name": "planFinDate",
                "source": "planFinDate",
                "type": "TEXT"
            },
            {
                "name": "planStartDate",
                "source": "planStartDate",
                "type": "TEXT"
            },
            {
                "name": "prjCode",
                "source": "prjCode",
                "type": "TEXT"
            },
            {
                "name": "prjName",
                "source": "prjName",
                "type": "TEXT"
            },
            {
                "name": "provinceCode",
                "source": "provinceCode",
                "type": "TEXT"
            },
            {
                "name": "provinceName",
                "source": "provinceName",
                "type": "TEXT"
            },
            {
                "name": "singleProjectCode",
                "source": "singleProjectCode",
                "type": "TEXT"
            },
            {
                "name": "singleProjectName",
                "source": "singleProjectName",
                "type": "TEXT"
            },
            {
                "name": "sortNum",
                "source": "sortNum",
                "type": "TEXT"
            },
            {
                "name": "status",
                "source": "status",
                "type": "TEXT"
            },
            {
                "name": "traceId",
                "source": "traceId",
                "type": "TEXT"
            }
        ],
        "dataset_key": "dataset_0e8c85a2",
        "key_candidates": [
            "id",
            "prjCode",
            "singleProjectCode",
            "biddingSectionCode",
            "prjCode+singleProjectCode+biddingSectionCode"
        ],
        "page_name": "监理项目部",
        "parent_record_path": "raw_event.sinPrjDTOS[]",
        "partition_field": "prjCode",
        "partition_key": "prjCode",
        "plugin_id": "dcp-dataset-0e8c85a2",
        "record_path": "raw_event.sinPrjDTOS[].bidSectDTOS[]",
        "record_type": "querySupervisorDeptProject:raw_event.sinPrjDTOS[].bidSectDTOS[]",
        "table": "canonical_p044_page_0e8c85a2__querysupervisordeptproject__raw_event_sinprjdtos_items_bidsectdtos_items"
    },
    {
        "api_name": "completion_acceptance_list",
        "api_path": "/apit/ebuild2-domain-project-stage/v1/completionAcceptance/getInfo",
        "columns": [
            {
                "name": "canUpload",
                "source": "canUpload",
                "type": "INTEGER"
            },
            {
                "name": "constrTransformerCapacity",
                "source": "constrTransformerCapacity",
                "type": "REAL"
            },
            {
                "name": "constructionLineLength",
                "source": "constructionLineLength",
                "type": "TEXT"
            },
            {
                "name": "extra",
                "source": "extra",
                "type": "TEXT"
            },
            {
                "name": "prjCode",
                "source": "prjCode",
                "type": "TEXT"
            },
            {
                "name": "prjName",
                "source": "prjName",
                "type": "TEXT"
            },
            {
                "name": "traceId",
                "source": "traceId",
                "type": "TEXT"
            },
            {
                "name": "voltageLevel",
                "source": "voltageLevel",
                "type": "TEXT"
            },
            {
                "name": "voltageLevelText",
                "source": "voltageLevelText",
                "type": "TEXT"
            }
        ],
        "dataset_key": "dataset_3a1b7207",
        "key_candidates": [
            "prjCode"
        ],
        "page_name": "竣工预验收",
        "parent_record_path": null,
        "partition_field": "prjCode",
        "partition_key": "prjCode",
        "plugin_id": "dcp-dataset-3a1b7207",
        "record_path": "raw_event",
        "record_type": "completion_acceptance_list:raw_event",
        "table": "canonical_p045_page_3a1b7207__completion_acceptance_list__raw_event"
    },
    {
        "api_name": "completion_acceptance_list",
        "api_path": "/apit/ebuild2-domain-project-stage/v1/completionAcceptance/getInfo",
        "columns": [
            {
                "name": "actualCommencementDate",
                "source": "actualCommencementDate",
                "type": "INTEGER"
            },
            {
                "name": "actualProgress",
                "source": "actualProgress",
                "type": "INTEGER"
            },
            {
                "name": "bidSectId",
                "source": "bidSectId",
                "type": "TEXT"
            },
            {
                "name": "biddingSectionCode",
                "source": "biddingSectionCode",
                "type": "TEXT"
            },
            {
                "name": "biddingSectionName",
                "source": "biddingSectionName",
                "type": "TEXT"
            },
            {
                "name": "completionDate",
                "source": "completionDate",
                "type": "TEXT"
            },
            {
                "name": "completionStatus",
                "source": "completionStatus",
                "type": "INTEGER"
            },
            {
                "name": "constructionStatus",
                "source": "constructionStatus",
                "type": "TEXT"
            },
            {
                "name": "extra",
                "source": "extra",
                "type": "TEXT"
            },
            {
                "name": "id",
                "source": "id",
                "type": "TEXT"
            },
            {
                "name": "preAccComplTime",
                "source": "preAccComplTime",
                "type": "TEXT"
            },
            {
                "name": "prjCode",
                "source": "prjCode",
                "type": "TEXT"
            },
            {
                "name": "seeFlag",
                "source": "seeFlag",
                "type": "INTEGER"
            },
            {
                "name": "sinPrjId",
                "source": "sinPrjId",
                "type": "TEXT"
            },
            {
                "name": "singleManagementFlag",
                "source": "singleManagementFlag",
                "type": "INTEGER"
            },
            {
                "name": "singleProjectCode",
                "source": "singleProjectCode",
                "type": "TEXT"
            },
            {
                "name": "singleProjectName",
                "source": "singleProjectName",
                "type": "TEXT"
            },
            {
                "name": "traceId",
                "source": "traceId",
                "type": "TEXT"
            }
        ],
        "dataset_key": "dataset_3a1b7207",
        "key_candidates": [
            "id",
            "prjCode",
            "singleProjectCode",
            "biddingSectionCode",
            "prjCode+singleProjectCode+biddingSectionCode"
        ],
        "page_name": "竣工预验收",
        "parent_record_path": "raw_event",
        "partition_field": "prjCode",
        "partition_key": "prjCode",
        "plugin_id": "dcp-dataset-3a1b7207",
        "record_path": "raw_event.preAcceptanceDTOList[]",
        "record_type": "completion_acceptance_list:raw_event.preAcceptanceDTOList[]",
        "table": "canonical_p045_page_3a1b7207__completion_acceptance_list__raw_event_preacceptancedtolist_items"
    },
    {
        "api_name": "completion_acceptance_list",
        "api_path": "/apit/ebuild2-domain-project-stage/v1/completionAcceptance/getInfo",
        "columns": [
            {
                "name": "acceptanceId",
                "source": "acceptanceId",
                "type": "TEXT"
            },
            {
                "name": "extra",
                "source": "extra",
                "type": "TEXT"
            },
            {
                "name": "fileId",
                "source": "fileId",
                "type": "TEXT"
            },
            {
                "name": "fileName",
                "source": "fileName",
                "type": "TEXT"
            },
            {
                "name": "fileTypeCode",
                "source": "fileTypeCode",
                "type": "INTEGER"
            },
            {
                "name": "id",
                "source": "id",
                "type": "TEXT"
            },
            {
                "name": "traceId",
                "source": "traceId",
                "type": "TEXT"
            }
        ],
        "dataset_key": "dataset_3a1b7207",
        "key_candidates": [
            "id"
        ],
        "page_name": "竣工预验收",
        "parent_record_path": "raw_event.preAcceptanceDTOList[]",
        "partition_field": null,
        "partition_key": null,
        "plugin_id": "dcp-dataset-3a1b7207",
        "record_path": "raw_event.preAcceptanceDTOList[].fileDTOList[]",
        "record_type": "completion_acceptance_list:raw_event.preAcceptanceDTOList[].fileDTOList[]",
        "table": "canonical_p045_page_3a1b7207__completion_acceptance_list__raw_event_preacceptancedtolist_items_filedtolist"
    },
    {
        "api_name": "completion_acceptance_list",
        "api_path": "/apit/ebuild2-domain-project-stage/v1/completionAcceptance/getInfo",
        "columns": [
            {
                "name": "extra",
                "source": "extra",
                "type": "TEXT"
            },
            {
                "name": "fileDTOList",
                "source": "fileDTOList",
                "type": "TEXT"
            },
            {
                "name": "fileNum",
                "source": "fileNum",
                "type": "INTEGER"
            },
            {
                "name": "fileType",
                "source": "fileType",
                "type": "INTEGER"
            },
            {
                "name": "fileTypeName",
                "source": "fileTypeName",
                "type": "TEXT"
            },
            {
                "name": "traceId",
                "source": "traceId",
                "type": "TEXT"
            }
        ],
        "dataset_key": "dataset_3a1b7207",
        "key_candidates": [
            "source_record_key+record_path"
        ],
        "page_name": "竣工预验收",
        "parent_record_path": "raw_event.preAcceptanceDTOList[]",
        "partition_field": null,
        "partition_key": null,
        "plugin_id": "dcp-dataset-3a1b7207",
        "record_path": "raw_event.preAcceptanceDTOList[].fileVOList[]",
        "record_type": "completion_acceptance_list:raw_event.preAcceptanceDTOList[].fileVOList[]",
        "table": "canonical_p045_page_3a1b7207__completion_acceptance_list__raw_event_preacceptancedtolist_items_filevolist_"
    },
    {
        "api_name": "completion_acceptance_list",
        "api_path": "/apit/ebuild2-domain-project-stage/v1/completionAcceptance/getInfo",
        "columns": [
            {
                "name": "acceptanceId",
                "source": "acceptanceId",
                "type": "TEXT"
            },
            {
                "name": "extra",
                "source": "extra",
                "type": "TEXT"
            },
            {
                "name": "fileId",
                "source": "fileId",
                "type": "TEXT"
            },
            {
                "name": "fileName",
                "source": "fileName",
                "type": "TEXT"
            },
            {
                "name": "fileTypeCode",
                "source": "fileTypeCode",
                "type": "INTEGER"
            },
            {
                "name": "id",
                "source": "id",
                "type": "TEXT"
            },
            {
                "name": "traceId",
                "source": "traceId",
                "type": "TEXT"
            }
        ],
        "dataset_key": "dataset_3a1b7207",
        "key_candidates": [
            "id"
        ],
        "page_name": "竣工预验收",
        "parent_record_path": "raw_event.preAcceptanceDTOList[].fileVOList[]",
        "partition_field": null,
        "partition_key": null,
        "plugin_id": "dcp-dataset-3a1b7207",
        "record_path": "raw_event.preAcceptanceDTOList[].fileVOList[].fileDTOList[]",
        "record_type": "completion_acceptance_list:raw_event.preAcceptanceDTOList[].fileVOList[].fileDTOList[]",
        "table": "canonical_p045_page_3a1b7207__completion_acceptance_list__raw_event_preacceptancedtolist_items_filevolist_"
    },
    {
        "api_name": "completion_acceptance_list",
        "api_path": "/apit/ebuild2-domain-project-stage/v1/completionAcceptance/getInfo",
        "columns": [
            {
                "name": "actualCommencementDate",
                "source": "actualCommencementDate",
                "type": "INTEGER"
            },
            {
                "name": "actualProgress",
                "source": "actualProgress",
                "type": "INTEGER"
            },
            {
                "name": "bidSectId",
                "source": "bidSectId",
                "type": "TEXT"
            },
            {
                "name": "biddingSectionCode",
                "source": "biddingSectionCode",
                "type": "TEXT"
            },
            {
                "name": "biddingSectionName",
                "source": "biddingSectionName",
                "type": "TEXT"
            },
            {
                "name": "completionDate",
                "source": "completionDate",
                "type": "TEXT"
            },
            {
                "name": "completionStatus",
                "source": "completionStatus",
                "type": "INTEGER"
            },
            {
                "name": "constructionStatus",
                "source": "constructionStatus",
                "type": "TEXT"
            },
            {
                "name": "extra",
                "source": "extra",
                "type": "TEXT"
            },
            {
                "name": "fileDTOList",
                "source": "fileDTOList",
                "type": "TEXT"
            },
            {
                "name": "id",
                "source": "id",
                "type": "TEXT"
            },
            {
                "name": "preAccComplTime",
                "source": "preAccComplTime",
                "type": "TEXT"
            },
            {
                "name": "preAcceptanceDTOList",
                "source": "preAcceptanceDTOList",
                "type": "TEXT"
            },
            {
                "name": "prjCode",
                "source": "prjCode",
                "type": "TEXT"
            },
            {
                "name": "seeFlag",
                "source": "seeFlag",
                "type": "INTEGER"
            },
            {
                "name": "sinPrjId",
                "source": "sinPrjId",
                "type": "TEXT"
            },
            {
                "name": "singleManagementFlag",
                "source": "singleManagementFlag",
                "type": "TEXT"
            },
            {
                "name": "singleProjectCode",
                "source": "singleProjectCode",
                "type": "TEXT"
            },
            {
                "name": "singleProjectName",
                "source": "singleProjectName",
                "type": "TEXT"
            },
            {
                "name": "traceId",
                "source": "traceId",
                "type": "TEXT"
            }
        ],
        "dataset_key": "dataset_3a1b7207",
        "key_candidates": [
            "id",
            "prjCode",
            "singleProjectCode",
            "biddingSectionCode",
            "prjCode+singleProjectCode+biddingSectionCode"
        ],
        "page_name": "竣工预验收",
        "parent_record_path": "raw_event.preAcceptanceDTOList[]",
        "partition_field": "prjCode",
        "partition_key": "prjCode",
        "plugin_id": "dcp-dataset-3a1b7207",
        "record_path": "raw_event.preAcceptanceDTOList[].preAcceptanceDTOList[]",
        "record_type": "completion_acceptance_list:raw_event.preAcceptanceDTOList[].preAcceptanceDTOList[]",
        "table": "canonical_p045_page_3a1b7207__completion_acceptance_list__raw_event_preacceptancedtolist_items_preacceptan"
    },
    {
        "api_name": "completion_acceptance_list",
        "api_path": "/apit/ebuild2-domain-project-stage/v1/completionAcceptance/getInfo",
        "columns": [
            {
                "name": "extra",
                "source": "extra",
                "type": "TEXT"
            },
            {
                "name": "fileDTOList",
                "source": "fileDTOList",
                "type": "TEXT"
            },
            {
                "name": "fileNum",
                "source": "fileNum",
                "type": "INTEGER"
            },
            {
                "name": "fileType",
                "source": "fileType",
                "type": "INTEGER"
            },
            {
                "name": "fileTypeName",
                "source": "fileTypeName",
                "type": "TEXT"
            },
            {
                "name": "traceId",
                "source": "traceId",
                "type": "TEXT"
            }
        ],
        "dataset_key": "dataset_3a1b7207",
        "key_candidates": [
            "source_record_key+record_path"
        ],
        "page_name": "竣工预验收",
        "parent_record_path": "raw_event.preAcceptanceDTOList[].preAcceptanceDTOList[]",
        "partition_field": null,
        "partition_key": null,
        "plugin_id": "dcp-dataset-3a1b7207",
        "record_path": "raw_event.preAcceptanceDTOList[].preAcceptanceDTOList[].fileVOList[]",
        "record_type": "completion_acceptance_list:raw_event.preAcceptanceDTOList[].preAcceptanceDTOList[].fileVOList[]",
        "table": "canonical_p045_page_3a1b7207__completion_acceptance_list__raw_event_preacceptancedtolist_items_preacceptan"
    },
    {
        "api_name": "completion_acceptance_details",
        "api_path": "/apit/ebuild2-domain-project-stage/v1/completionAcceptance/geQrySinAndBidInfo",
        "columns": [
            {
                "name": "actualCommencementDate",
                "source": "actualCommencementDate",
                "type": "INTEGER"
            },
            {
                "name": "actualProgress",
                "source": "actualProgress",
                "type": "REAL"
            },
            {
                "name": "bidSectId",
                "source": "bidSectId",
                "type": "TEXT"
            },
            {
                "name": "biddingSectionCode",
                "source": "biddingSectionCode",
                "type": "TEXT"
            },
            {
                "name": "biddingSectionName",
                "source": "biddingSectionName",
                "type": "TEXT"
            },
            {
                "name": "completionDate",
                "source": "completionDate",
                "type": "TEXT"
            },
            {
                "name": "completionStatus",
                "source": "completionStatus",
                "type": "INTEGER"
            },
            {
                "name": "constructionStatus",
                "source": "constructionStatus",
                "type": "INTEGER"
            },
            {
                "name": "extra",
                "source": "extra",
                "type": "TEXT"
            },
            {
                "name": "fileDTOList",
                "source": "fileDTOList",
                "type": "TEXT"
            },
            {
                "name": "id",
                "source": "id",
                "type": "TEXT"
            },
            {
                "name": "preAccComplTime",
                "source": "preAccComplTime",
                "type": "TEXT"
            },
            {
                "name": "prjCode",
                "source": "prjCode",
                "type": "TEXT"
            },
            {
                "name": "seeFlag",
                "source": "seeFlag",
                "type": "INTEGER"
            },
            {
                "name": "sinPrjId",
                "source": "sinPrjId",
                "type": "TEXT"
            },
            {
                "name": "singleManagementFlag",
                "source": "singleManagementFlag",
                "type": "INTEGER"
            },
            {
                "name": "singleProjectCode",
                "source": "singleProjectCode",
                "type": "TEXT"
            },
            {
                "name": "singleProjectName",
                "source": "singleProjectName",
                "type": "TEXT"
            },
            {
                "name": "traceId",
                "source": "traceId",
                "type": "TEXT"
            }
        ],
        "dataset_key": "dataset_3a1b7207",
        "key_candidates": [
            "id",
            "prjCode",
            "singleProjectCode",
            "biddingSectionCode",
            "prjCode+singleProjectCode+biddingSectionCode"
        ],
        "page_name": "竣工预验收",
        "parent_record_path": null,
        "partition_field": "prjCode",
        "partition_key": "prjCode",
        "plugin_id": "dcp-dataset-3a1b7207",
        "record_path": "raw_event",
        "record_type": "completion_acceptance_details:raw_event",
        "table": "canonical_p045_page_3a1b7207__completion_acceptance_details__raw_event"
    },
    {
        "api_name": "completion_acceptance_details",
        "api_path": "/apit/ebuild2-domain-project-stage/v1/completionAcceptance/geQrySinAndBidInfo",
        "columns": [
            {
                "name": "extra",
                "source": "extra",
                "type": "TEXT"
            },
            {
                "name": "fileDTOList",
                "source": "fileDTOList",
                "type": "TEXT"
            },
            {
                "name": "fileNum",
                "source": "fileNum",
                "type": "INTEGER"
            },
            {
                "name": "fileType",
                "source": "fileType",
                "type": "INTEGER"
            },
            {
                "name": "fileTypeName",
                "source": "fileTypeName",
                "type": "TEXT"
            },
            {
                "name": "traceId",
                "source": "traceId",
                "type": "TEXT"
            }
        ],
        "dataset_key": "dataset_3a1b7207",
        "key_candidates": [
            "source_record_key+record_path"
        ],
        "page_name": "竣工预验收",
        "parent_record_path": "raw_event",
        "partition_field": null,
        "partition_key": null,
        "plugin_id": "dcp-dataset-3a1b7207",
        "record_path": "raw_event.fileVOList[]",
        "record_type": "completion_acceptance_details:raw_event.fileVOList[]",
        "table": "canonical_p045_page_3a1b7207__completion_acceptance_details__raw_event_filevolist_items"
    },
    {
        "api_name": "completion_acceptance_details",
        "api_path": "/apit/ebuild2-domain-project-stage/v1/completionAcceptance/geQrySinAndBidInfo",
        "columns": [
            {
                "name": "actualCommencementDate",
                "source": "actualCommencementDate",
                "type": "INTEGER"
            },
            {
                "name": "actualProgress",
                "source": "actualProgress",
                "type": "REAL"
            },
            {
                "name": "bidSectId",
                "source": "bidSectId",
                "type": "TEXT"
            },
            {
                "name": "biddingSectionCode",
                "source": "biddingSectionCode",
                "type": "TEXT"
            },
            {
                "name": "biddingSectionName",
                "source": "biddingSectionName",
                "type": "TEXT"
            },
            {
                "name": "completionDate",
                "source": "completionDate",
                "type": "TEXT"
            },
            {
                "name": "completionStatus",
                "source": "completionStatus",
                "type": "INTEGER"
            },
            {
                "name": "constructionStatus",
                "source": "constructionStatus",
                "type": "INTEGER"
            },
            {
                "name": "extra",
                "source": "extra",
                "type": "TEXT"
            },
            {
                "name": "fileDTOList",
                "source": "fileDTOList",
                "type": "TEXT"
            },
            {
                "name": "id",
                "source": "id",
                "type": "TEXT"
            },
            {
                "name": "preAccComplTime",
                "source": "preAccComplTime",
                "type": "TEXT"
            },
            {
                "name": "preAcceptanceDTOList",
                "source": "preAcceptanceDTOList",
                "type": "TEXT"
            },
            {
                "name": "prjCode",
                "source": "prjCode",
                "type": "TEXT"
            },
            {
                "name": "seeFlag",
                "source": "seeFlag",
                "type": "INTEGER"
            },
            {
                "name": "sinPrjId",
                "source": "sinPrjId",
                "type": "TEXT"
            },
            {
                "name": "singleManagementFlag",
                "source": "singleManagementFlag",
                "type": "TEXT"
            },
            {
                "name": "singleProjectCode",
                "source": "singleProjectCode",
                "type": "TEXT"
            },
            {
                "name": "singleProjectName",
                "source": "singleProjectName",
                "type": "TEXT"
            },
            {
                "name": "traceId",
                "source": "traceId",
                "type": "TEXT"
            }
        ],
        "dataset_key": "dataset_3a1b7207",
        "key_candidates": [
            "id",
            "prjCode",
            "singleProjectCode",
            "biddingSectionCode",
            "prjCode+singleProjectCode+biddingSectionCode"
        ],
        "page_name": "竣工预验收",
        "parent_record_path": "raw_event",
        "partition_field": "prjCode",
        "partition_key": "prjCode",
        "plugin_id": "dcp-dataset-3a1b7207",
        "record_path": "raw_event.preAcceptanceDTOList[]",
        "record_type": "completion_acceptance_details:raw_event.preAcceptanceDTOList[]",
        "table": "canonical_p045_page_3a1b7207__completion_acceptance_details__raw_event_preacceptancedtolist_items"
    },
    {
        "api_name": "completion_acceptance_details",
        "api_path": "/apit/ebuild2-domain-project-stage/v1/completionAcceptance/geQrySinAndBidInfo",
        "columns": [
            {
                "name": "extra",
                "source": "extra",
                "type": "TEXT"
            },
            {
                "name": "fileDTOList",
                "source": "fileDTOList",
                "type": "TEXT"
            },
            {
                "name": "fileNum",
                "source": "fileNum",
                "type": "INTEGER"
            },
            {
                "name": "fileType",
                "source": "fileType",
                "type": "INTEGER"
            },
            {
                "name": "fileTypeName",
                "source": "fileTypeName",
                "type": "TEXT"
            },
            {
                "name": "traceId",
                "source": "traceId",
                "type": "TEXT"
            }
        ],
        "dataset_key": "dataset_3a1b7207",
        "key_candidates": [
            "source_record_key+record_path"
        ],
        "page_name": "竣工预验收",
        "parent_record_path": "raw_event.preAcceptanceDTOList[]",
        "partition_field": null,
        "partition_key": null,
        "plugin_id": "dcp-dataset-3a1b7207",
        "record_path": "raw_event.preAcceptanceDTOList[].fileVOList[]",
        "record_type": "completion_acceptance_details:raw_event.preAcceptanceDTOList[].fileVOList[]",
        "table": "canonical_p045_page_3a1b7207__completion_acceptance_details__raw_event_preacceptancedtolist_items_filevolist_"
    },
    {
        "api_name": "plan_completion_reports",
        "api_path": "/apit/ebuild2-domain-plan-statistics/v1/projectInventory/queryProjectInventoryList",
        "columns": [
            {
                "name": "actualCommencementDate",
                "source": "actualCommencementDate",
                "type": "TEXT"
            },
            {
                "name": "actualCommissioningDate",
                "source": "actualCommissioningDate",
                "type": "TEXT"
            },
            {
                "name": "buildUnitCode",
                "source": "buildUnitCode",
                "type": "TEXT"
            },
            {
                "name": "buildUnitName",
                "source": "buildUnitName",
                "type": "TEXT"
            },
            {
                "name": "commenceMonthNum",
                "source": "commenceMonthNum",
                "type": "REAL"
            },
            {
                "name": "completeLineLength",
                "source": "completeLineLength",
                "type": "REAL"
            },
            {
                "name": "completeTransCapacity",
                "source": "completeTransCapacity",
                "type": "REAL"
            },
            {
                "name": "isUhvProject",
                "source": "isUhvProject",
                "type": "INTEGER"
            },
            {
                "name": "planCommenceTime",
                "source": "planCommenceTime",
                "type": "TEXT"
            },
            {
                "name": "planExecuteType",
                "source": "planExecuteType",
                "type": "INTEGER"
            },
            {
                "name": "planLineLength",
                "source": "planLineLength",
                "type": "REAL"
            },
            {
                "name": "planProdTime",
                "source": "planProdTime",
                "type": "TEXT"
            },
            {
                "name": "planTransCapacity",
                "source": "planTransCapacity",
                "type": "REAL"
            },
            {
                "name": "prjCode",
                "source": "prjCode",
                "type": "TEXT"
            },
            {
                "name": "prjName",
                "source": "prjName",
                "type": "TEXT"
            },
            {
                "name": "provinceCode",
                "source": "provinceCode",
                "type": "TEXT"
            },
            {
                "name": "provinceName",
                "source": "provinceName",
                "type": "TEXT"
            },
            {
                "name": "serialNumber",
                "source": "serialNumber",
                "type": "TEXT"
            },
            {
                "name": "sinPrjInventoryList",
                "source": "sinPrjInventoryList",
                "type": "TEXT"
            },
            {
                "name": "singleProjectCode",
                "source": "singleProjectCode",
                "type": "TEXT"
            },
            {
                "name": "singleProjectName",
                "source": "singleProjectName",
                "type": "TEXT"
            },
            {
                "name": "voltageLevelCode",
                "source": "voltageLevelCode",
                "type": "TEXT"
            },
            {
                "name": "voltageLevelName",
                "source": "voltageLevelName",
                "type": "TEXT"
            }
        ],
        "dataset_key": "dataset_b7dcfdb4",
        "key_candidates": [
            "prjCode",
            "singleProjectCode",
            "prjCode+singleProjectCode"
        ],
        "page_name": "计划完成情况统计",
        "parent_record_path": null,
        "partition_field": "prjCode",
        "partition_key": "prjCode",
        "plugin_id": "dcp-dataset-b7dcfdb4",
        "record_path": "raw_event",
        "record_type": "plan_completion_reports:raw_event",
        "table": "canonical_p046_page_b7dcfdb4__plan_completion_reports__raw_event"
    },
    {
        "api_name": "design_change_approval",
        "api_path": "/apit/ebuild2-domain-economy-manage/v1/changeApproval/changeApprovalPage",
        "columns": [
            {
                "name": "approvVisaFlag",
                "source": "approvVisaFlag",
                "type": "INTEGER"
            },
            {
                "name": "approvalFormNumber",
                "source": "approvalFormNumber",
                "type": "TEXT"
            },
            {
                "name": "approvalOpinion",
                "source": "approvalOpinion",
                "type": "TEXT"
            },
            {
                "name": "automaticFlag",
                "source": "automaticFlag",
                "type": "TEXT"
            },
            {
                "name": "biddingSectionCode",
                "source": "biddingSectionCode",
                "type": "TEXT"
            },
            {
                "name": "biddingSectionName",
                "source": "biddingSectionName",
                "type": "TEXT"
            },
            {
                "name": "bpmId",
                "source": "bpmId",
                "type": "TEXT"
            },
            {
                "name": "buildDeptId",
                "source": "buildDeptId",
                "type": "TEXT"
            },
            {
                "name": "buildDeptName",
                "source": "buildDeptName",
                "type": "TEXT"
            },
            {
                "name": "buildUnitEmReviewOpinion",
                "source": "buildUnitEmReviewOpinion",
                "type": "TEXT"
            },
            {
                "name": "buildUnitLeaderRevDate",
                "source": "buildUnitLeaderRevDate",
                "type": "TEXT"
            },
            {
                "name": "buildUnitLeaderRevOpn",
                "source": "buildUnitLeaderRevOpn",
                "type": "TEXT"
            },
            {
                "name": "buildUnitManagerRevDate",
                "source": "buildUnitManagerRevDate",
                "type": "TEXT"
            },
            {
                "name": "buildUnitManagerRevOpn",
                "source": "buildUnitManagerRevOpn",
                "type": "TEXT"
            },
            {
                "name": "buildUnitTeReviewOpinion",
                "source": "buildUnitTeReviewOpinion",
                "type": "TEXT"
            },
            {
                "name": "buildUnitTmReviewOpinion",
                "source": "buildUnitTmReviewOpinion",
                "type": "TEXT"
            },
            {
                "name": "changeApprovalFileId",
                "source": "changeApprovalFileId",
                "type": "TEXT"
            },
            {
                "name": "changeContactId",
                "source": "changeContactId",
                "type": "TEXT"
            },
            {
                "name": "changesAmount",
                "source": "changesAmount",
                "type": "TEXT"
            },
            {
                "name": "changesCause",
                "source": "changesCause",
                "type": "TEXT"
            },
            {
                "name": "changesReason",
                "source": "changesReason",
                "type": "INTEGER"
            },
            {
                "name": "changesReasonName",
                "source": "changesReasonName",
                "type": "TEXT"
            },
            {
                "name": "changesType",
                "source": "changesType",
                "type": "INTEGER"
            },
            {
                "name": "changesTypeName",
                "source": "changesTypeName",
                "type": "TEXT"
            },
            {
                "name": "checkDate",
                "source": "checkDate",
                "type": "TEXT"
            },
            {
                "name": "constrPrjDeptRevOpinion",
                "source": "constrPrjDeptRevOpinion",
                "type": "TEXT"
            },
            {
                "name": "constrPrjDeptReviewDate",
                "source": "constrPrjDeptReviewDate",
                "type": "TEXT"
            },
            {
                "name": "contactButtonFlag",
                "source": "contactButtonFlag",
                "type": "INTEGER"
            },
            {
                "name": "contactNumber",
                "source": "contactNumber",
                "type": "TEXT"
            },
            {
                "name": "createTime",
                "source": "createTime",
                "type": "TEXT"
            },
            {
                "name": "createrId",
                "source": "createrId",
                "type": "TEXT"
            },
            {
                "name": "curRoleCode",
                "source": "curRoleCode",
                "type": "TEXT"
            },
            {
                "name": "delFlag",
                "source": "delFlag",
                "type": "INTEGER"
            },
            {
                "name": "deptType",
                "source": "deptType",
                "type": "TEXT"
            },
            {
                "name": "designPrjDeptReviewDate",
                "source": "designPrjDeptReviewDate",
                "type": "TEXT"
            },
            {
                "name": "drawBackFlag",
                "source": "drawBackFlag",
                "type": "INTEGER"
            },
            {
                "name": "editVisaFlag",
                "source": "editVisaFlag",
                "type": "INTEGER"
            },
            {
                "name": "extra",
                "source": "extra",
                "type": "TEXT"
            },
            {
                "name": "flowName",
                "source": "flowName",
                "type": "TEXT"
            },
            {
                "name": "flowRole",
                "source": "flowRole",
                "type": "TEXT"
            },
            {
                "name": "id",
                "source": "id",
                "type": "TEXT"
            },
            {
                "name": "initiateDate",
                "source": "initiateDate",
                "type": "TEXT"
            },
            {
                "name": "inspectionButtonFlag",
                "source": "inspectionButtonFlag",
                "type": "INTEGER"
            },
            {
                "name": "inspectionNumber",
                "source": "inspectionNumber",
                "type": "TEXT"
            },
            {
                "name": "inspectionReportId",
                "source": "inspectionReportId",
                "type": "TEXT"
            },
            {
                "name": "instanceId",
                "source": "instanceId",
                "type": "TEXT"
            },
            {
                "name": "instructionId",
                "source": "instructionId",
                "type": "TEXT"
            },
            {
                "name": "lastRoleFlag",
                "source": "lastRoleFlag",
                "type": "INTEGER"
            },
            {
                "name": "netType",
                "source": "netType",
                "type": "TEXT"
            },
            {
                "name": "nextNodeIndex",
                "source": "nextNodeIndex",
                "type": "TEXT"
            },
            {
                "name": "oaApplyStatus",
                "source": "oaApplyStatus",
                "type": "TEXT"
            },
            {
                "name": "otherReasonText",
                "source": "otherReasonText",
                "type": "TEXT"
            },
            {
                "name": "ownerPrjDeptReviewDate",
                "source": "ownerPrjDeptReviewDate",
                "type": "TEXT"
            },
            {
                "name": "ownerPrjDeptReviewOpinion",
                "source": "ownerPrjDeptReviewOpinion",
                "type": "TEXT"
            },
            {
                "name": "ownerPrjZjReviewOpn",
                "source": "ownerPrjZjReviewOpn",
                "type": "TEXT"
            },
            {
                "name": "pickFlag",
                "source": "pickFlag",
                "type": "INTEGER"
            },
            {
                "name": "postCode",
                "source": "postCode",
                "type": "TEXT"
            },
            {
                "name": "postName",
                "source": "postName",
                "type": "TEXT"
            },
            {
                "name": "prjCode",
                "source": "prjCode",
                "type": "TEXT"
            },
            {
                "name": "prjSupervisionDeptRevDate",
                "source": "prjSupervisionDeptRevDate",
                "type": "TEXT"
            },
            {
                "name": "prjSupervisionDeptRevOpn",
                "source": "prjSupervisionDeptRevOpn",
                "type": "TEXT"
            },
            {
                "name": "provinceEmReviewOpinion",
                "source": "provinceEmReviewOpinion",
                "type": "TEXT"
            },
            {
                "name": "provinceLeaderReviewDate",
                "source": "provinceLeaderReviewDate",
                "type": "TEXT"
            },
            {
                "name": "provinceLeaderReviewOpn",
                "source": "provinceLeaderReviewOpn",
                "type": "TEXT"
            },
            {
                "name": "provinceTeReviewOpinion",
                "source": "provinceTeReviewOpinion",
                "type": "TEXT"
            },
            {
                "name": "realName",
                "source": "realName",
                "type": "TEXT"
            },
            {
                "name": "reviewStatus",
                "source": "reviewStatus",
                "type": "INTEGER"
            },
            {
                "name": "reviewStatusName",
                "source": "reviewStatusName",
                "type": "TEXT"
            },
            {
                "name": "roleCode",
                "source": "roleCode",
                "type": "TEXT"
            },
            {
                "name": "selfUserId",
                "source": "selfUserId",
                "type": "TEXT"
            },
            {
                "name": "signStatus",
                "source": "signStatus",
                "type": "INTEGER"
            },
            {
                "name": "singleProjectCode",
                "source": "singleProjectCode",
                "type": "TEXT"
            },
            {
                "name": "singleProjectName",
                "source": "singleProjectName",
                "type": "TEXT"
            },
            {
                "name": "submitFlag",
                "source": "submitFlag",
                "type": "INTEGER"
            },
            {
                "name": "supervisionDeptName",
                "source": "supervisionDeptName",
                "type": "TEXT"
            },
            {
                "name": "supervisionPrjDeptId",
                "source": "supervisionPrjDeptId",
                "type": "TEXT"
            },
            {
                "name": "taskAssignButtonFlag",
                "source": "taskAssignButtonFlag",
                "type": "INTEGER"
            },
            {
                "name": "traceId",
                "source": "traceId",
                "type": "TEXT"
            },
            {
                "name": "unitCode",
                "source": "unitCode",
                "type": "TEXT"
            },
            {
                "name": "updateTime",
                "source": "updateTime",
                "type": "TEXT"
            },
            {
                "name": "updaterId",
                "source": "updaterId",
                "type": "TEXT"
            },
            {
                "name": "viewVisaFlag",
                "source": "viewVisaFlag",
                "type": "INTEGER"
            },
            {
                "name": "xh",
                "source": "xh",
                "type": "TEXT"
            }
        ],
        "dataset_key": "dataset_8a28eaaf",
        "key_candidates": [
            "id",
            "prjCode",
            "singleProjectCode",
            "biddingSectionCode",
            "prjCode+singleProjectCode+biddingSectionCode"
        ],
        "page_name": "设计变更审批单",
        "parent_record_path": null,
        "partition_field": "prjCode",
        "partition_key": "prjCode",
        "plugin_id": "dcp-dataset-8a28eaaf",
        "record_path": "raw_event",
        "record_type": "design_change_approval:raw_event",
        "table": "canonical_p049_page_8a28eaaf__design_change_approval__raw_event"
    },
    {
        "api_name": "countDesignDealData",
        "api_path": "/apit/ebuild2-domain-economy-manage/v1/changeApproval/countDesignDealData",
        "columns": [
            {
                "name": "allCount",
                "source": "allCount",
                "type": "INTEGER"
            },
            {
                "name": "approvingCount",
                "source": "approvingCount",
                "type": "INTEGER"
            },
            {
                "name": "completedCount",
                "source": "completedCount",
                "type": "INTEGER"
            },
            {
                "name": "extra",
                "source": "extra",
                "type": "TEXT"
            },
            {
                "name": "ownHandleCount",
                "source": "ownHandleCount",
                "type": "INTEGER"
            },
            {
                "name": "refusedCount",
                "source": "refusedCount",
                "type": "INTEGER"
            },
            {
                "name": "refusedShowFlag",
                "source": "refusedShowFlag",
                "type": "TEXT"
            },
            {
                "name": "showContractFlag",
                "source": "showContractFlag",
                "type": "TEXT"
            },
            {
                "name": "showPurchaseFlag",
                "source": "showPurchaseFlag",
                "type": "TEXT"
            },
            {
                "name": "traceId",
                "source": "traceId",
                "type": "TEXT"
            },
            {
                "name": "unitCode",
                "source": "unitCode",
                "type": "TEXT"
            },
            {
                "name": "waitHandleCount",
                "source": "waitHandleCount",
                "type": "INTEGER"
            }
        ],
        "dataset_key": "dataset_8a28eaaf",
        "key_candidates": [
            "source_record_key+record_path"
        ],
        "page_name": "设计变更审批单",
        "parent_record_path": null,
        "partition_field": null,
        "partition_key": null,
        "plugin_id": "dcp-dataset-8a28eaaf",
        "record_path": "raw_event",
        "record_type": "countDesignDealData:raw_event",
        "table": "canonical_p049_page_8a28eaaf__countdesigndealdata__raw_event"
    },
    {
        "api_name": "design_dept_list",
        "api_path": "/apit/ebuild2-domain-project-form/v1/designDept/queryDeptListAPP",
        "columns": [
            {
                "name": "address",
                "source": "address",
                "type": "TEXT"
            },
            {
                "name": "affiliationCode",
                "source": "affiliationCode",
                "type": "TEXT"
            },
            {
                "name": "affiliationName",
                "source": "affiliationName",
                "type": "TEXT"
            },
            {
                "name": "bpmId",
                "source": "bpmId",
                "type": "TEXT"
            },
            {
                "name": "buildUnitCode",
                "source": "buildUnitCode",
                "type": "TEXT"
            },
            {
                "name": "contactTelephone",
                "source": "contactTelephone",
                "type": "TEXT"
            },
            {
                "name": "createTime",
                "source": "createTime",
                "type": "INTEGER"
            },
            {
                "name": "createrId",
                "source": "createrId",
                "type": "TEXT"
            },
            {
                "name": "deleteFlag",
                "source": "deleteFlag",
                "type": "INTEGER"
            },
            {
                "name": "departmentStatus",
                "source": "departmentStatus",
                "type": "INTEGER"
            },
            {
                "name": "departmentType",
                "source": "departmentType",
                "type": "INTEGER"
            },
            {
                "name": "deptCitiesCode",
                "source": "deptCitiesCode",
                "type": "INTEGER"
            },
            {
                "name": "deptCitiesName",
                "source": "deptCitiesName",
                "type": "TEXT"
            },
            {
                "name": "deptDistrictCode",
                "source": "deptDistrictCode",
                "type": "INTEGER"
            },
            {
                "name": "deptDistrictName",
                "source": "deptDistrictName",
                "type": "TEXT"
            },
            {
                "name": "deptId",
                "source": "deptId",
                "type": "TEXT"
            },
            {
                "name": "deptProvinceCode",
                "source": "deptProvinceCode",
                "type": "TEXT"
            },
            {
                "name": "deptProvinceName",
                "source": "deptProvinceName",
                "type": "TEXT"
            },
            {
                "name": "emailAddress",
                "source": "emailAddress",
                "type": "TEXT"
            },
            {
                "name": "establishmentDate",
                "source": "establishmentDate",
                "type": "TEXT"
            },
            {
                "name": "extra",
                "source": "extra",
                "type": "TEXT"
            },
            {
                "name": "faxNo",
                "source": "faxNo",
                "type": "TEXT"
            },
            {
                "name": "groupMarkup",
                "source": "groupMarkup",
                "type": "TEXT"
            },
            {
                "name": "historyFlag",
                "source": "historyFlag",
                "type": "INTEGER"
            },
            {
                "name": "isHaveReset",
                "source": "isHaveReset",
                "type": "TEXT"
            },
            {
                "name": "postalCode",
                "source": "postalCode",
                "type": "TEXT"
            },
            {
                "name": "projectDepartmentName",
                "source": "projectDepartmentName",
                "type": "TEXT"
            },
            {
                "name": "projectDeptNo",
                "source": "projectDeptNo",
                "type": "TEXT"
            },
            {
                "name": "provinceCode",
                "source": "provinceCode",
                "type": "TEXT"
            },
            {
                "name": "realName",
                "source": "realName",
                "type": "TEXT"
            },
            {
                "name": "singnFlag",
                "source": "singnFlag",
                "type": "TEXT"
            },
            {
                "name": "traceId",
                "source": "traceId",
                "type": "TEXT"
            },
            {
                "name": "updateTime",
                "source": "updateTime",
                "type": "INTEGER"
            },
            {
                "name": "updaterId",
                "source": "updaterId",
                "type": "TEXT"
            },
            {
                "name": "year",
                "source": "year",
                "type": "TEXT"
            }
        ],
        "dataset_key": "dataset_2981b5b1",
        "key_candidates": [
            "source_record_key+record_path"
        ],
        "page_name": "设计项目部",
        "parent_record_path": null,
        "partition_field": null,
        "partition_key": null,
        "plugin_id": "dcp-dataset-2981b5b1",
        "record_path": "raw_event",
        "record_type": "design_dept_list:raw_event",
        "table": "canonical_p050_page_2981b5b1__design_dept_list__raw_event"
    },
    {
        "api_name": "design_dept_personnel",
        "api_path": "/apit/ebuild2-domain-project-form/v1/designPerson/queryDesignDeptPerson",
        "columns": [
            {
                "name": "beforeId",
                "source": "beforeId",
                "type": "TEXT"
            },
            {
                "name": "beforeName",
                "source": "beforeName",
                "type": "TEXT"
            },
            {
                "name": "buildername",
                "source": "buildername",
                "type": "TEXT"
            },
            {
                "name": "changeFlag",
                "source": "changeFlag",
                "type": "TEXT"
            },
            {
                "name": "deleteFlag",
                "source": "deleteFlag",
                "type": "TEXT"
            },
            {
                "name": "deptKey",
                "source": "deptKey",
                "type": "INTEGER"
            },
            {
                "name": "dprId",
                "source": "dprId",
                "type": "TEXT"
            },
            {
                "name": "engineerRecordId",
                "source": "engineerRecordId",
                "type": "TEXT"
            },
            {
                "name": "entryDate",
                "source": "entryDate",
                "type": "TEXT"
            },
            {
                "name": "exitDate",
                "source": "exitDate",
                "type": "TEXT"
            },
            {
                "name": "extra",
                "source": "extra",
                "type": "TEXT"
            },
            {
                "name": "gender",
                "source": "gender",
                "type": "TEXT"
            },
            {
                "name": "id",
                "source": "id",
                "type": "TEXT"
            },
            {
                "name": "idCard",
                "source": "idCard",
                "type": "TEXT"
            },
            {
                "name": "jobCode",
                "source": "jobCode",
                "type": "TEXT"
            },
            {
                "name": "jobName",
                "source": "jobName",
                "type": "TEXT"
            },
            {
                "name": "mobile",
                "source": "mobile",
                "type": "TEXT"
            },
            {
                "name": "personnelCap",
                "source": "personnelCap",
                "type": "INTEGER"
            },
            {
                "name": "positionCode",
                "source": "positionCode",
                "type": "TEXT"
            },
            {
                "name": "positionName",
                "source": "positionName",
                "type": "TEXT"
            },
            {
                "name": "provinceCode",
                "source": "provinceCode",
                "type": "TEXT"
            },
            {
                "name": "realName",
                "source": "realName",
                "type": "TEXT"
            },
            {
                "name": "specialty",
                "source": "specialty",
                "type": "TEXT"
            },
            {
                "name": "statusState",
                "source": "statusState",
                "type": "INTEGER"
            },
            {
                "name": "traceId",
                "source": "traceId",
                "type": "TEXT"
            },
            {
                "name": "unitName",
                "source": "unitName",
                "type": "TEXT"
            },
            {
                "name": "withinFlag",
                "source": "withinFlag",
                "type": "TEXT"
            }
        ],
        "dataset_key": "dataset_2981b5b1",
        "key_candidates": [
            "id"
        ],
        "page_name": "设计项目部",
        "parent_record_path": null,
        "partition_field": null,
        "partition_key": null,
        "plugin_id": "dcp-dataset-2981b5b1",
        "record_path": "raw_event",
        "record_type": "design_dept_personnel:raw_event",
        "table": "canonical_p050_page_2981b5b1__design_dept_personnel__raw_event"
    },
    {
        "api_name": "design_dept_personnel",
        "api_path": "/apit/ebuild2-domain-project-form/v1/designPerson/queryDesignDeptPerson",
        "columns": [
            {
                "name": "certId",
                "source": "certId",
                "type": "TEXT"
            },
            {
                "name": "certName",
                "source": "certName",
                "type": "TEXT"
            },
            {
                "name": "certNameText",
                "source": "certNameText",
                "type": "TEXT"
            },
            {
                "name": "certStatus",
                "source": "certStatus",
                "type": "INTEGER"
            },
            {
                "name": "certType",
                "source": "certType",
                "type": "TEXT"
            },
            {
                "name": "certTypeText",
                "source": "certTypeText",
                "type": "TEXT"
            },
            {
                "name": "createTime",
                "source": "createTime",
                "type": "TEXT"
            },
            {
                "name": "createrId",
                "source": "createrId",
                "type": "TEXT"
            },
            {
                "name": "deleteFlag",
                "source": "deleteFlag",
                "type": "TEXT"
            },
            {
                "name": "deptId",
                "source": "deptId",
                "type": "TEXT"
            },
            {
                "name": "extra",
                "source": "extra",
                "type": "TEXT"
            },
            {
                "name": "id",
                "source": "id",
                "type": "TEXT"
            },
            {
                "name": "jobCode",
                "source": "jobCode",
                "type": "TEXT"
            },
            {
                "name": "jobName",
                "source": "jobName",
                "type": "TEXT"
            },
            {
                "name": "personnelId",
                "source": "personnelId",
                "type": "TEXT"
            },
            {
                "name": "traceId",
                "source": "traceId",
                "type": "TEXT"
            },
            {
                "name": "updateTime",
                "source": "updateTime",
                "type": "TEXT"
            },
            {
                "name": "updaterId",
                "source": "updaterId",
                "type": "TEXT"
            },
            {
                "name": "validEndDate",
                "source": "validEndDate",
                "type": "TEXT"
            }
        ],
        "dataset_key": "dataset_2981b5b1",
        "key_candidates": [
            "id"
        ],
        "page_name": "设计项目部",
        "parent_record_path": "raw_event",
        "partition_field": null,
        "partition_key": null,
        "plugin_id": "dcp-dataset-2981b5b1",
        "record_path": "raw_event.certificates[]",
        "record_type": "design_dept_personnel:raw_event.certificates[]",
        "table": "canonical_p050_page_2981b5b1__design_dept_personnel__raw_event_certificates_items"
    },
    {
        "api_name": "queryDesignDeptFile",
        "api_path": "/apit/ebuild2-domain-project-form/v1/designDept/queryDesignDeptFile",
        "columns": [
            {
                "name": "approvalNode",
                "source": "approvalNode",
                "type": "INTEGER"
            },
            {
                "name": "authorizationMatter",
                "source": "authorizationMatter",
                "type": "TEXT"
            },
            {
                "name": "certificateName",
                "source": "certificateName",
                "type": "TEXT"
            },
            {
                "name": "certificateNo",
                "source": "certificateNo",
                "type": "TEXT"
            },
            {
                "name": "deleteFlag",
                "source": "deleteFlag",
                "type": "INTEGER"
            },
            {
                "name": "documentClass",
                "source": "documentClass",
                "type": "INTEGER"
            },
            {
                "name": "extra",
                "source": "extra",
                "type": "TEXT"
            },
            {
                "name": "fileId",
                "source": "fileId",
                "type": "TEXT"
            },
            {
                "name": "fileName",
                "source": "fileName",
                "type": "TEXT"
            },
            {
                "name": "id",
                "source": "id",
                "type": "TEXT"
            },
            {
                "name": "instanceId",
                "source": "instanceId",
                "type": "TEXT"
            },
            {
                "name": "isHaveReset",
                "source": "isHaveReset",
                "type": "TEXT"
            },
            {
                "name": "personnelId",
                "source": "personnelId",
                "type": "TEXT"
            },
            {
                "name": "practiceQualification",
                "source": "practiceQualification",
                "type": "TEXT"
            },
            {
                "name": "prjCode",
                "source": "prjCode",
                "type": "TEXT"
            },
            {
                "name": "prjName",
                "source": "prjName",
                "type": "TEXT"
            },
            {
                "name": "projectDepartmentId",
                "source": "projectDepartmentId",
                "type": "TEXT"
            },
            {
                "name": "signTime",
                "source": "signTime",
                "type": "TEXT"
            },
            {
                "name": "signatureFlag",
                "source": "signatureFlag",
                "type": "INTEGER"
            },
            {
                "name": "signaturesStatus",
                "source": "signaturesStatus",
                "type": "INTEGER"
            },
            {
                "name": "singnFlag",
                "source": "singnFlag",
                "type": "INTEGER"
            },
            {
                "name": "traceId",
                "source": "traceId",
                "type": "TEXT"
            }
        ],
        "dataset_key": "dataset_2981b5b1",
        "key_candidates": [
            "id",
            "prjCode"
        ],
        "page_name": "设计项目部",
        "parent_record_path": null,
        "partition_field": "prjCode",
        "partition_key": "prjCode",
        "plugin_id": "dcp-dataset-2981b5b1",
        "record_path": "raw_event",
        "record_type": "queryDesignDeptFile:raw_event",
        "table": "canonical_p050_page_2981b5b1__querydesigndeptfile__raw_event"
    },
    {
        "api_name": "queryDesignDeptProject",
        "api_path": "/apit/ebuild2-domain-project-form/v1/designProject/queryDesignDeptProject",
        "columns": [
            {
                "name": "actualCommencementDate",
                "source": "actualCommencementDate",
                "type": "TEXT"
            },
            {
                "name": "constrTransformerCapacity",
                "source": "constrTransformerCapacity",
                "type": "REAL"
            },
            {
                "name": "constructionLineLength",
                "source": "constructionLineLength",
                "type": "TEXT"
            },
            {
                "name": "extra",
                "source": "extra",
                "type": "TEXT"
            },
            {
                "name": "isDeptManage",
                "source": "isDeptManage",
                "type": "TEXT"
            },
            {
                "name": "plannedCommencementDate",
                "source": "plannedCommencementDate",
                "type": "TEXT"
            },
            {
                "name": "plannedCommissioningDate",
                "source": "plannedCommissioningDate",
                "type": "TEXT"
            },
            {
                "name": "prjCode",
                "source": "prjCode",
                "type": "TEXT"
            },
            {
                "name": "prjName",
                "source": "prjName",
                "type": "TEXT"
            },
            {
                "name": "projectManagement",
                "source": "projectManagement",
                "type": "TEXT"
            },
            {
                "name": "sortNum",
                "source": "sortNum",
                "type": "TEXT"
            },
            {
                "name": "traceId",
                "source": "traceId",
                "type": "TEXT"
            },
            {
                "name": "voltageLevel",
                "source": "voltageLevel",
                "type": "TEXT"
            },
            {
                "name": "voltageLevelText",
                "source": "voltageLevelText",
                "type": "TEXT"
            }
        ],
        "dataset_key": "dataset_2981b5b1",
        "key_candidates": [
            "prjCode"
        ],
        "page_name": "设计项目部",
        "parent_record_path": null,
        "partition_field": "prjCode",
        "partition_key": "prjCode",
        "plugin_id": "dcp-dataset-2981b5b1",
        "record_path": "raw_event",
        "record_type": "queryDesignDeptProject:raw_event",
        "table": "canonical_p050_page_2981b5b1__querydesigndeptproject__raw_event"
    },
    {
        "api_name": "queryDesignDeptProject",
        "api_path": "/apit/ebuild2-domain-project-form/v1/designProject/queryDesignDeptProject",
        "columns": [
            {
                "name": "actualCommencementDate",
                "source": "actualCommencementDate",
                "type": "TEXT"
            },
            {
                "name": "bidSectDTOS",
                "source": "bidSectDTOS",
                "type": "TEXT"
            },
            {
                "name": "buildUnitCode",
                "source": "buildUnitCode",
                "type": "TEXT"
            },
            {
                "name": "buildUnitName",
                "source": "buildUnitName",
                "type": "TEXT"
            },
            {
                "name": "constrNature",
                "source": "constrNature",
                "type": "INTEGER"
            },
            {
                "name": "constrNatureText",
                "source": "constrNatureText",
                "type": "TEXT"
            },
            {
                "name": "constrTransformerCapacity",
                "source": "constrTransformerCapacity",
                "type": "REAL"
            },
            {
                "name": "constructionLineLength",
                "source": "constructionLineLength",
                "type": "TEXT"
            },
            {
                "name": "contractId",
                "source": "contractId",
                "type": "TEXT"
            },
            {
                "name": "extra",
                "source": "extra",
                "type": "TEXT"
            },
            {
                "name": "personnelDTOS",
                "source": "personnelDTOS",
                "type": "TEXT"
            },
            {
                "name": "plannedCommencementDate",
                "source": "plannedCommencementDate",
                "type": "TEXT"
            },
            {
                "name": "plannedCommissioningDate",
                "source": "plannedCommissioningDate",
                "type": "TEXT"
            },
            {
                "name": "prjCode",
                "source": "prjCode",
                "type": "TEXT"
            },
            {
                "name": "prjName",
                "source": "prjName",
                "type": "TEXT"
            },
            {
                "name": "projectManagement",
                "source": "projectManagement",
                "type": "TEXT"
            },
            {
                "name": "provinceCode",
                "source": "provinceCode",
                "type": "TEXT"
            },
            {
                "name": "provinceName",
                "source": "provinceName",
                "type": "TEXT"
            },
            {
                "name": "singleProjectCode",
                "source": "singleProjectCode",
                "type": "TEXT"
            },
            {
                "name": "singleProjectName",
                "source": "singleProjectName",
                "type": "TEXT"
            },
            {
                "name": "sortNum",
                "source": "sortNum",
                "type": "TEXT"
            },
            {
                "name": "traceId",
                "source": "traceId",
                "type": "TEXT"
            },
            {
                "name": "voltageLevel",
                "source": "voltageLevel",
                "type": "TEXT"
            }
        ],
        "dataset_key": "dataset_2981b5b1",
        "key_candidates": [
            "prjCode",
            "singleProjectCode",
            "prjCode+singleProjectCode"
        ],
        "page_name": "设计项目部",
        "parent_record_path": "raw_event",
        "partition_field": "prjCode",
        "partition_key": "prjCode",
        "plugin_id": "dcp-dataset-2981b5b1",
        "record_path": "raw_event.sinPrjDTOS[]",
        "record_type": "queryDesignDeptProject:raw_event.sinPrjDTOS[]",
        "table": "canonical_p050_page_2981b5b1__querydesigndeptproject__raw_event_sinprjdtos_items"
    },
    {
        "api_name": "queryWorkItemInitList",
        "api_path": "/apit/ebuild2-domain-quality-manage/v1/init/queryWorkItemInitList",
        "columns": [
            {
                "name": "checkItemName",
                "source": "checkItemName",
                "type": "TEXT"
            },
            {
                "name": "checkReport",
                "source": "checkReport",
                "type": "INTEGER"
            },
            {
                "name": "checkStandard",
                "source": "checkStandard",
                "type": "TEXT"
            },
            {
                "name": "constrMgtUnitCode",
                "source": "constrMgtUnitCode",
                "type": "TEXT"
            },
            {
                "name": "deviceName",
                "source": "deviceName",
                "type": "TEXT"
            },
            {
                "name": "deviceType",
                "source": "deviceType",
                "type": "INTEGER"
            },
            {
                "name": "engType",
                "source": "engType",
                "type": "INTEGER"
            },
            {
                "name": "fileNum",
                "source": "fileNum",
                "type": "TEXT"
            },
            {
                "name": "id",
                "source": "id",
                "type": "TEXT"
            },
            {
                "name": "itemCheckId",
                "source": "itemCheckId",
                "type": "TEXT"
            },
            {
                "name": "number",
                "source": "number",
                "type": "INTEGER"
            },
            {
                "name": "openFlag",
                "source": "openFlag",
                "type": "INTEGER"
            },
            {
                "name": "partName",
                "source": "partName",
                "type": "TEXT"
            },
            {
                "name": "problemSetsNum",
                "source": "problemSetsNum",
                "type": "TEXT"
            },
            {
                "name": "productionMake",
                "source": "productionMake",
                "type": "INTEGER"
            },
            {
                "name": "provinceCode",
                "source": "provinceCode",
                "type": "TEXT"
            },
            {
                "name": "randomTest",
                "source": "randomTest",
                "type": "INTEGER"
            },
            {
                "name": "schduleId",
                "source": "schduleId",
                "type": "TEXT"
            },
            {
                "name": "sinPrjCode",
                "source": "sinPrjCode",
                "type": "TEXT"
            },
            {
                "name": "techView",
                "source": "techView",
                "type": "INTEGER"
            },
            {
                "name": "testDate",
                "source": "testDate",
                "type": "TEXT"
            },
            {
                "name": "testSetsNum",
                "source": "testSetsNum",
                "type": "TEXT"
            },
            {
                "name": "workItemId",
                "source": "workItemId",
                "type": "TEXT"
            }
        ],
        "dataset_key": "dataset_726638d3",
        "key_candidates": [
            "id"
        ],
        "page_name": "质量检测计划",
        "parent_record_path": null,
        "partition_field": null,
        "partition_key": null,
        "plugin_id": "dcp-dataset-726638d3",
        "record_path": "raw_event",
        "record_type": "queryWorkItemInitList:raw_event",
        "table": "canonical_p053_page_726638d3__queryworkiteminitlist__raw_event"
    },
    {
        "api_name": "getCheckCountTitle",
        "api_path": "/apit/ebuild2-domain-quality-accept/v1/checkCount/getCheckCountTitle",
        "columns": [
            {
                "name": "accuracyRate",
                "source": "accuracyRate",
                "type": "TEXT"
            },
            {
                "name": "alreadyCount",
                "source": "alreadyCount",
                "type": "INTEGER"
            },
            {
                "name": "checkRate",
                "source": "checkRate",
                "type": "TEXT"
            },
            {
                "name": "extra",
                "source": "extra",
                "type": "TEXT"
            },
            {
                "name": "filledCount",
                "source": "filledCount",
                "type": "INTEGER"
            },
            {
                "name": "oughtCount",
                "source": "oughtCount",
                "type": "INTEGER"
            },
            {
                "name": "qualifiedCount",
                "source": "qualifiedCount",
                "type": "INTEGER"
            },
            {
                "name": "traceId",
                "source": "traceId",
                "type": "TEXT"
            }
        ],
        "dataset_key": "dataset_784b6267",
        "key_candidates": [
            "source_record_key+record_path"
        ],
        "page_name": "质量验收汇总",
        "parent_record_path": null,
        "partition_field": null,
        "partition_key": null,
        "plugin_id": "dcp-dataset-784b6267",
        "record_path": "raw_event",
        "record_type": "getCheckCountTitle:raw_event",
        "table": "canonical_p054_page_784b6267__getcheckcounttitle__raw_event"
    },
    {
        "api_name": "getCheckCountList",
        "api_path": "/apit/ebuild2-domain-quality-accept/v1/checkCount/getCheckCountList",
        "columns": [
            {
                "name": "accuracyRate",
                "source": "accuracyRate",
                "type": "TEXT"
            },
            {
                "name": "alreadyCount",
                "source": "alreadyCount",
                "type": "INTEGER"
            },
            {
                "name": "bidSectCode",
                "source": "bidSectCode",
                "type": "TEXT"
            },
            {
                "name": "bidSectName",
                "source": "bidSectName",
                "type": "TEXT"
            },
            {
                "name": "checkRate",
                "source": "checkRate",
                "type": "TEXT"
            },
            {
                "name": "divideDataName",
                "source": "divideDataName",
                "type": "TEXT"
            },
            {
                "name": "divideDataType",
                "source": "divideDataType",
                "type": "TEXT"
            },
            {
                "name": "divideDataTypeName",
                "source": "divideDataTypeName",
                "type": "TEXT"
            },
            {
                "name": "extra",
                "source": "extra",
                "type": "TEXT"
            },
            {
                "name": "filledCount",
                "source": "filledCount",
                "type": "INTEGER"
            },
            {
                "name": "id",
                "source": "id",
                "type": "TEXT"
            },
            {
                "name": "oughtCount",
                "source": "oughtCount",
                "type": "INTEGER"
            },
            {
                "name": "prjCode",
                "source": "prjCode",
                "type": "TEXT"
            },
            {
                "name": "provinceCode",
                "source": "provinceCode",
                "type": "TEXT"
            },
            {
                "name": "qualifiedCount",
                "source": "qualifiedCount",
                "type": "INTEGER"
            },
            {
                "name": "thresholdAccept",
                "source": "thresholdAccept",
                "type": "TEXT"
            },
            {
                "name": "traceId",
                "source": "traceId",
                "type": "TEXT"
            },
            {
                "name": "voltageLevel",
                "source": "voltageLevel",
                "type": "TEXT"
            },
            {
                "name": "year",
                "source": "year",
                "type": "TEXT"
            }
        ],
        "dataset_key": "dataset_784b6267",
        "key_candidates": [
            "id",
            "prjCode"
        ],
        "page_name": "质量验收汇总",
        "parent_record_path": null,
        "partition_field": "prjCode",
        "partition_key": "prjCode",
        "plugin_id": "dcp-dataset-784b6267",
        "record_path": "raw_event",
        "record_type": "getCheckCountList:raw_event",
        "table": "canonical_p054_page_784b6267__getcheckcountlist__raw_event"
    },
    {
        "api_name": "queryProjectInfoListPage",
        "api_path": "/apit/ebuild2-domain-project-form/v1/projectInformation/queryProjectInfoListPage",
        "columns": [
            {
                "name": "actualCommencementDate",
                "source": "actualCommencementDate",
                "type": "TEXT"
            },
            {
                "name": "actualCommissioningDate",
                "source": "actualCommissioningDate",
                "type": "TEXT"
            },
            {
                "name": "buildUnitCode",
                "source": "buildUnitCode",
                "type": "TEXT"
            },
            {
                "name": "buildUnitName",
                "source": "buildUnitName",
                "type": "TEXT"
            },
            {
                "name": "constrNature",
                "source": "constrNature",
                "type": "TEXT"
            },
            {
                "name": "constrNatureName",
                "source": "constrNatureName",
                "type": "TEXT"
            },
            {
                "name": "constrTransformerCapacity",
                "source": "constrTransformerCapacity",
                "type": "TEXT"
            },
            {
                "name": "constructionBidWinningDate",
                "source": "constructionBidWinningDate",
                "type": "TEXT"
            },
            {
                "name": "constructionLineLength",
                "source": "constructionLineLength",
                "type": "TEXT"
            },
            {
                "name": "initialApprovalDate",
                "source": "initialApprovalDate",
                "type": "TEXT"
            },
            {
                "name": "plannedCommencementDate",
                "source": "plannedCommencementDate",
                "type": "TEXT"
            },
            {
                "name": "plannedCommissioningDate",
                "source": "plannedCommissioningDate",
                "type": "TEXT"
            },
            {
                "name": "prjCode",
                "source": "prjCode",
                "type": "TEXT"
            },
            {
                "name": "prjName",
                "source": "prjName",
                "type": "TEXT"
            },
            {
                "name": "projectNature",
                "source": "projectNature",
                "type": "TEXT"
            },
            {
                "name": "projectStatusName",
                "source": "projectStatusName",
                "type": "TEXT"
            },
            {
                "name": "projectType",
                "source": "projectType",
                "type": "TEXT"
            },
            {
                "name": "projectTypeName",
                "source": "projectTypeName",
                "type": "TEXT"
            },
            {
                "name": "provinceCode",
                "source": "provinceCode",
                "type": "TEXT"
            },
            {
                "name": "provinceName",
                "source": "provinceName",
                "type": "TEXT"
            },
            {
                "name": "serialNumber",
                "source": "serialNumber",
                "type": "TEXT"
            },
            {
                "name": "singleProjectCounts",
                "source": "singleProjectCounts",
                "type": "INTEGER"
            },
            {
                "name": "singleProjectList",
                "source": "singleProjectList",
                "type": "TEXT"
            },
            {
                "name": "voltageLevel",
                "source": "voltageLevel",
                "type": "TEXT"
            },
            {
                "name": "voltageLevelName",
                "source": "voltageLevelName",
                "type": "TEXT"
            }
        ],
        "dataset_key": "dataset_eac2e191",
        "key_candidates": [
            "prjCode"
        ],
        "page_name": "项目信息查询",
        "parent_record_path": null,
        "partition_field": "prjCode",
        "partition_key": "prjCode",
        "plugin_id": "dcp-dataset-eac2e191",
        "record_path": "raw_event",
        "record_type": "queryProjectInfoListPage:raw_event",
        "table": "canonical_p055_page_eac2e191__queryprojectinfolistpage__raw_event"
    },
    {
        "api_name": "project_reserve_pool",
        "api_path": "/apit/ebuild2-domain-project-form/v1/preparation/getReserveInfo",
        "columns": [
            {
                "name": "apprFileNo",
                "source": "apprFileNo",
                "type": "TEXT"
            },
            {
                "name": "buildUnitCode",
                "source": "buildUnitCode",
                "type": "TEXT"
            },
            {
                "name": "buildUnitName",
                "source": "buildUnitName",
                "type": "TEXT"
            },
            {
                "name": "buildingExpenses",
                "source": "buildingExpenses",
                "type": "TEXT"
            },
            {
                "name": "constrAddress",
                "source": "constrAddress",
                "type": "TEXT"
            },
            {
                "name": "constrLineLength",
                "source": "constrLineLength",
                "type": "TEXT"
            },
            {
                "name": "constrNature",
                "source": "constrNature",
                "type": "TEXT"
            },
            {
                "name": "constrTransCapacity",
                "source": "constrTransCapacity",
                "type": "TEXT"
            },
            {
                "name": "createTime",
                "source": "createTime",
                "type": "TEXT"
            },
            {
                "name": "createrId",
                "source": "createrId",
                "type": "TEXT"
            },
            {
                "name": "deleteFlag",
                "source": "deleteFlag",
                "type": "INTEGER"
            },
            {
                "name": "earlierStageFile",
                "source": "earlierStageFile",
                "type": "TEXT"
            },
            {
                "name": "equipmentAcquisitionExpenses",
                "source": "equipmentAcquisitionExpenses",
                "type": "REAL"
            },
            {
                "name": "extra",
                "source": "extra",
                "type": "TEXT"
            },
            {
                "name": "feaDinvest",
                "source": "feaDinvest",
                "type": "REAL"
            },
            {
                "name": "feaSinvest",
                "source": "feaSinvest",
                "type": "REAL"
            },
            {
                "name": "id",
                "source": "id",
                "type": "TEXT"
            },
            {
                "name": "installationExpenses",
                "source": "installationExpenses",
                "type": "REAL"
            },
            {
                "name": "landExpropriationExpenses",
                "source": "landExpropriationExpenses",
                "type": "REAL"
            },
            {
                "name": "natureInvestment",
                "source": "natureInvestment",
                "type": "TEXT"
            },
            {
                "name": "num",
                "source": "num",
                "type": "TEXT"
            },
            {
                "name": "otherExpenses",
                "source": "otherExpenses",
                "type": "REAL"
            },
            {
                "name": "preparationExpenses",
                "source": "preparationExpenses",
                "type": "TEXT"
            },
            {
                "name": "prjCode",
                "source": "prjCode",
                "type": "TEXT"
            },
            {
                "name": "prjName",
                "source": "prjName",
                "type": "TEXT"
            },
            {
                "name": "prjStatus",
                "source": "prjStatus",
                "type": "INTEGER"
            },
            {
                "name": "projectApprovalDocumentNo",
                "source": "projectApprovalDocumentNo",
                "type": "TEXT"
            },
            {
                "name": "projectCenterBuildUnitCode",
                "source": "projectCenterBuildUnitCode",
                "type": "TEXT"
            },
            {
                "name": "projectCenterConstrNature",
                "source": "projectCenterConstrNature",
                "type": "TEXT"
            },
            {
                "name": "projectCenterProvinceCode",
                "source": "projectCenterProvinceCode",
                "type": "TEXT"
            },
            {
                "name": "projectVersion",
                "source": "projectVersion",
                "type": "TEXT"
            },
            {
                "name": "provideUnit",
                "source": "provideUnit",
                "type": "TEXT"
            },
            {
                "name": "provinceCode",
                "source": "provinceCode",
                "type": "TEXT"
            },
            {
                "name": "provinceName",
                "source": "provinceName",
                "type": "TEXT"
            },
            {
                "name": "sinDTOList",
                "source": "sinDTOList",
                "type": "TEXT"
            },
            {
                "name": "traceId",
                "source": "traceId",
                "type": "TEXT"
            },
            {
                "name": "updateTime",
                "source": "updateTime",
                "type": "TEXT"
            },
            {
                "name": "updaterId",
                "source": "updaterId",
                "type": "TEXT"
            },
            {
                "name": "voltageLevel",
                "source": "voltageLevel",
                "type": "TEXT"
            },
            {
                "name": "voltageLevelName",
                "source": "voltageLevelName",
                "type": "TEXT"
            },
            {
                "name": "weaveDTOList",
                "source": "weaveDTOList",
                "type": "TEXT"
            }
        ],
        "dataset_key": "dataset_26f597c7",
        "key_candidates": [
            "id",
            "prjCode"
        ],
        "page_name": "项目储备库查看",
        "parent_record_path": null,
        "partition_field": "prjCode",
        "partition_key": "prjCode",
        "plugin_id": "dcp-dataset-26f597c7",
        "record_path": "raw_event",
        "record_type": "project_reserve_pool:raw_event",
        "table": "canonical_p056_page_26f597c7__project_reserve_pool__raw_event"
    },
    {
        "api_name": "preconstruction_results_detail",
        "api_path": "/apit/ebuild2-domain-project-form/v1/projectInfoGet/one/queryDetail",
        "columns": [
            {
                "name": "actualCommencementDate",
                "source": "actualCommencementDate",
                "type": "TEXT"
            },
            {
                "name": "actualCommissioningDate",
                "source": "actualCommissioningDate",
                "type": "TEXT"
            },
            {
                "name": "actualComplDate",
                "source": "actualComplDate",
                "type": "TEXT"
            },
            {
                "name": "apprFileNo",
                "source": "apprFileNo",
                "type": "TEXT"
            },
            {
                "name": "buildUnitCode",
                "source": "buildUnitCode",
                "type": "TEXT"
            },
            {
                "name": "buildUnitName",
                "source": "buildUnitName",
                "type": "TEXT"
            },
            {
                "name": "constrAddress",
                "source": "constrAddress",
                "type": "TEXT"
            },
            {
                "name": "constrNature",
                "source": "constrNature",
                "type": "INTEGER"
            },
            {
                "name": "constrNatureName",
                "source": "constrNatureName",
                "type": "TEXT"
            },
            {
                "name": "constrTransformerCapacity",
                "source": "constrTransformerCapacity",
                "type": "REAL"
            },
            {
                "name": "constructionCategory",
                "source": "constructionCategory",
                "type": "INTEGER"
            },
            {
                "name": "constructionCategoryName",
                "source": "constructionCategoryName",
                "type": "TEXT"
            },
            {
                "name": "constructionLineLength",
                "source": "constructionLineLength",
                "type": "TEXT"
            },
            {
                "name": "constructionStatus",
                "source": "constructionStatus",
                "type": "INTEGER"
            },
            {
                "name": "createTime",
                "source": "createTime",
                "type": "TEXT"
            },
            {
                "name": "createrId",
                "source": "createrId",
                "type": "TEXT"
            },
            {
                "name": "deleteButton",
                "source": "deleteButton",
                "type": "TEXT"
            },
            {
                "name": "deleteFlag",
                "source": "deleteFlag",
                "type": "INTEGER"
            },
            {
                "name": "deptStatus",
                "source": "deptStatus",
                "type": "INTEGER"
            },
            {
                "name": "earlierStageFile",
                "source": "earlierStageFile",
                "type": "TEXT"
            },
            {
                "name": "existsFlag",
                "source": "existsFlag",
                "type": "TEXT"
            },
            {
                "name": "extra",
                "source": "extra",
                "type": "TEXT"
            },
            {
                "name": "feaDinvest",
                "source": "feaDinvest",
                "type": "REAL"
            },
            {
                "name": "feaLineLength",
                "source": "feaLineLength",
                "type": "TEXT"
            },
            {
                "name": "feaSinvest",
                "source": "feaSinvest",
                "type": "REAL"
            },
            {
                "name": "feasTransCapacity",
                "source": "feasTransCapacity",
                "type": "REAL"
            },
            {
                "name": "id",
                "source": "id",
                "type": "TEXT"
            },
            {
                "name": "lineQuantity",
                "source": "lineQuantity",
                "type": "TEXT"
            },
            {
                "name": "locationArea",
                "source": "locationArea",
                "type": "TEXT"
            },
            {
                "name": "locationAreaName",
                "source": "locationAreaName",
                "type": "TEXT"
            },
            {
                "name": "locationMunicipality",
                "source": "locationMunicipality",
                "type": "TEXT"
            },
            {
                "name": "locationMunicipalityName",
                "source": "locationMunicipalityName",
                "type": "TEXT"
            },
            {
                "name": "locationProvince",
                "source": "locationProvince",
                "type": "TEXT"
            },
            {
                "name": "locationProvinceName",
                "source": "locationProvinceName",
                "type": "TEXT"
            },
            {
                "name": "mainTransformerQuantity",
                "source": "mainTransformerQuantity",
                "type": "INTEGER"
            },
            {
                "name": "nonConstrDepartmentImpl",
                "source": "nonConstrDepartmentImpl",
                "type": "INTEGER"
            },
            {
                "name": "num",
                "source": "num",
                "type": "TEXT"
            },
            {
                "name": "planComplDate",
                "source": "planComplDate",
                "type": "TEXT"
            },
            {
                "name": "plannedCommencementDate",
                "source": "plannedCommencementDate",
                "type": "TEXT"
            },
            {
                "name": "plannedCommissioningDate",
                "source": "plannedCommissioningDate",
                "type": "TEXT"
            },
            {
                "name": "prjCode",
                "source": "prjCode",
                "type": "TEXT"
            },
            {
                "name": "prjManageMode",
                "source": "prjManageMode",
                "type": "INTEGER"
            },
            {
                "name": "prjName",
                "source": "prjName",
                "type": "TEXT"
            },
            {
                "name": "prjSource",
                "source": "prjSource",
                "type": "INTEGER"
            },
            {
                "name": "prjStatus",
                "source": "prjStatus",
                "type": "TEXT"
            },
            {
                "name": "prodTransCapacity",
                "source": "prodTransCapacity",
                "type": "REAL"
            },
            {
                "name": "productionLineLength",
                "source": "productionLineLength",
                "type": "TEXT"
            },
            {
                "name": "projectApprovalDocumentNo",
                "source": "projectApprovalDocumentNo",
                "type": "TEXT"
            },
            {
                "name": "projectType",
                "source": "projectType",
                "type": "INTEGER"
            },
            {
                "name": "projectTypeName",
                "source": "projectTypeName",
                "type": "TEXT"
            },
            {
                "name": "provinceCode",
                "source": "provinceCode",
                "type": "TEXT"
            },
            {
                "name": "provinceName",
                "source": "provinceName",
                "type": "TEXT"
            },
            {
                "name": "pushStatus",
                "source": "pushStatus",
                "type": "TEXT"
            },
            {
                "name": "reserveButton",
                "source": "reserveButton",
                "type": "INTEGER"
            },
            {
                "name": "same",
                "source": "same",
                "type": "TEXT"
            },
            {
                "name": "sinDivideStatus",
                "source": "sinDivideStatus",
                "type": "TEXT"
            },
            {
                "name": "traceId",
                "source": "traceId",
                "type": "TEXT"
            },
            {
                "name": "updateTime",
                "source": "updateTime",
                "type": "TEXT"
            },
            {
                "name": "updaterId",
                "source": "updaterId",
                "type": "TEXT"
            },
            {
                "name": "voltageLevel",
                "source": "voltageLevel",
                "type": "TEXT"
            },
            {
                "name": "voltageLevelName",
                "source": "voltageLevelName",
                "type": "TEXT"
            }
        ],
        "dataset_key": "dataset_6ae53ddc",
        "key_candidates": [
            "id",
            "prjCode"
        ],
        "page_name": "项目前期成果",
        "parent_record_path": null,
        "partition_field": "prjCode",
        "partition_key": "prjCode",
        "plugin_id": "dcp-dataset-6ae53ddc",
        "record_path": "raw_event",
        "record_type": "preconstruction_results_detail:raw_event",
        "table": "canonical_p057_page_6ae53ddc__preconstruction_results_detail__raw_event"
    },
    {
        "api_name": "preconstruction_results_detail",
        "api_path": "/apit/ebuild2-domain-project-form/v1/projectInfoGet/one/queryDetail",
        "columns": [
            {
                "name": "actualCommencementDate",
                "source": "actualCommencementDate",
                "type": "TEXT"
            },
            {
                "name": "actualCommissioningDate",
                "source": "actualCommissioningDate",
                "type": "TEXT"
            },
            {
                "name": "actualCompletionDate",
                "source": "actualCompletionDate",
                "type": "TEXT"
            },
            {
                "name": "buildUnitCode",
                "source": "buildUnitCode",
                "type": "TEXT"
            },
            {
                "name": "buildUnitName",
                "source": "buildUnitName",
                "type": "TEXT"
            },
            {
                "name": "commencementOrderCount",
                "source": "commencementOrderCount",
                "type": "INTEGER"
            },
            {
                "name": "constrAddress",
                "source": "constrAddress",
                "type": "TEXT"
            },
            {
                "name": "constrNature",
                "source": "constrNature",
                "type": "INTEGER"
            },
            {
                "name": "constrNatureName",
                "source": "constrNatureName",
                "type": "TEXT"
            },
            {
                "name": "constrTransformerCapacity",
                "source": "constrTransformerCapacity",
                "type": "REAL"
            },
            {
                "name": "constructionLineLength",
                "source": "constructionLineLength",
                "type": "TEXT"
            },
            {
                "name": "constructionStatus",
                "source": "constructionStatus",
                "type": "INTEGER"
            },
            {
                "name": "createTime",
                "source": "createTime",
                "type": "TEXT"
            },
            {
                "name": "createrId",
                "source": "createrId",
                "type": "TEXT"
            },
            {
                "name": "deleteFlag",
                "source": "deleteFlag",
                "type": "INTEGER"
            },
            {
                "name": "extra",
                "source": "extra",
                "type": "TEXT"
            },
            {
                "name": "feaDinvest",
                "source": "feaDinvest",
                "type": "REAL"
            },
            {
                "name": "feaLineLength",
                "source": "feaLineLength",
                "type": "TEXT"
            },
            {
                "name": "feaSinvest",
                "source": "feaSinvest",
                "type": "REAL"
            },
            {
                "name": "feasTransCapacity",
                "source": "feasTransCapacity",
                "type": "TEXT"
            },
            {
                "name": "id",
                "source": "id",
                "type": "TEXT"
            },
            {
                "name": "integrateIntosysFlag",
                "source": "integrateIntosysFlag",
                "type": "INTEGER"
            },
            {
                "name": "itemId",
                "source": "itemId",
                "type": "TEXT"
            },
            {
                "name": "kfDeleteFlag",
                "source": "kfDeleteFlag",
                "type": "INTEGER"
            },
            {
                "name": "lineQuantity",
                "source": "lineQuantity",
                "type": "TEXT"
            },
            {
                "name": "locationArea",
                "source": "locationArea",
                "type": "TEXT"
            },
            {
                "name": "locationAreaName",
                "source": "locationAreaName",
                "type": "TEXT"
            },
            {
                "name": "locationMunicipality",
                "source": "locationMunicipality",
                "type": "TEXT"
            },
            {
                "name": "locationMunicipalityName",
                "source": "locationMunicipalityName",
                "type": "TEXT"
            },
            {
                "name": "locationProvince",
                "source": "locationProvince",
                "type": "TEXT"
            },
            {
                "name": "locationProvinceName",
                "source": "locationProvinceName",
                "type": "TEXT"
            },
            {
                "name": "mainTransformerQuantity",
                "source": "mainTransformerQuantity",
                "type": "INTEGER"
            },
            {
                "name": "num",
                "source": "num",
                "type": "TEXT"
            },
            {
                "name": "operationalPermissions",
                "source": "operationalPermissions",
                "type": "TEXT"
            },
            {
                "name": "parentItemId",
                "source": "parentItemId",
                "type": "TEXT"
            },
            {
                "name": "planComplDate",
                "source": "planComplDate",
                "type": "TEXT"
            },
            {
                "name": "plannedCommencementDate",
                "source": "plannedCommencementDate",
                "type": "TEXT"
            },
            {
                "name": "plannedCommissioningDate",
                "source": "plannedCommissioningDate",
                "type": "TEXT"
            },
            {
                "name": "prjCode",
                "source": "prjCode",
                "type": "TEXT"
            },
            {
                "name": "prjStatus",
                "source": "prjStatus",
                "type": "TEXT"
            },
            {
                "name": "prodTransCapacity",
                "source": "prodTransCapacity",
                "type": "REAL"
            },
            {
                "name": "productionLineLength",
                "source": "productionLineLength",
                "type": "TEXT"
            },
            {
                "name": "provinceCode",
                "source": "provinceCode",
                "type": "TEXT"
            },
            {
                "name": "provinceName",
                "source": "provinceName",
                "type": "TEXT"
            },
            {
                "name": "revokeStatus",
                "source": "revokeStatus",
                "type": "TEXT"
            },
            {
                "name": "sinProgress",
                "source": "sinProgress",
                "type": "TEXT"
            },
            {
                "name": "singleProjectCode",
                "source": "singleProjectCode",
                "type": "TEXT"
            },
            {
                "name": "singleProjectDetailsType",
                "source": "singleProjectDetailsType",
                "type": "INTEGER"
            },
            {
                "name": "singleProjectDetailsTypeName",
                "source": "singleProjectDetailsTypeName",
                "type": "TEXT"
            },
            {
                "name": "singleProjectName",
                "source": "singleProjectName",
                "type": "TEXT"
            },
            {
                "name": "singleProjectPrerType",
                "source": "singleProjectPrerType",
                "type": "TEXT"
            },
            {
                "name": "singleProjectPrerTypeName",
                "source": "singleProjectPrerTypeName",
                "type": "TEXT"
            },
            {
                "name": "singleProjectType",
                "source": "singleProjectType",
                "type": "INTEGER"
            },
            {
                "name": "singleProjectTypeName",
                "source": "singleProjectTypeName",
                "type": "TEXT"
            },
            {
                "name": "status",
                "source": "status",
                "type": "INTEGER"
            },
            {
                "name": "traceId",
                "source": "traceId",
                "type": "TEXT"
            },
            {
                "name": "updateTime",
                "source": "updateTime",
                "type": "TEXT"
            },
            {
                "name": "updaterId",
                "source": "updaterId",
                "type": "TEXT"
            },
            {
                "name": "voltageLevel",
                "source": "voltageLevel",
                "type": "TEXT"
            },
            {
                "name": "voltageLevelName",
                "source": "voltageLevelName",
                "type": "TEXT"
            }
        ],
        "dataset_key": "dataset_6ae53ddc",
        "key_candidates": [
            "id",
            "prjCode",
            "singleProjectCode",
            "prjCode+singleProjectCode"
        ],
        "page_name": "项目前期成果",
        "parent_record_path": "raw_event",
        "partition_field": "prjCode",
        "partition_key": "prjCode",
        "plugin_id": "dcp-dataset-6ae53ddc",
        "record_path": "raw_event.sinList[]",
        "record_type": "preconstruction_results_detail:raw_event.sinList[]",
        "table": "canonical_p057_page_6ae53ddc__preconstruction_results_detail__raw_event_sinlist_items"
    },
    {
        "api_name": "preconstruction_results_detail",
        "api_path": "/apit/ebuild2-domain-project-form/v1/projectInfoGet/one/queryDetail",
        "columns": [
            {
                "name": "createTime",
                "source": "createTime",
                "type": "TEXT"
            },
            {
                "name": "createrId",
                "source": "createrId",
                "type": "TEXT"
            },
            {
                "name": "deleteFlag",
                "source": "deleteFlag",
                "type": "INTEGER"
            },
            {
                "name": "extra",
                "source": "extra",
                "type": "TEXT"
            },
            {
                "name": "id",
                "source": "id",
                "type": "TEXT"
            },
            {
                "name": "prjCode",
                "source": "prjCode",
                "type": "TEXT"
            },
            {
                "name": "singleProjectCode",
                "source": "singleProjectCode",
                "type": "TEXT"
            },
            {
                "name": "taskDate",
                "source": "taskDate",
                "type": "TEXT"
            },
            {
                "name": "taskNameCode",
                "source": "taskNameCode",
                "type": "INTEGER"
            },
            {
                "name": "traceId",
                "source": "traceId",
                "type": "TEXT"
            },
            {
                "name": "updateTime",
                "source": "updateTime",
                "type": "TEXT"
            },
            {
                "name": "updaterId",
                "source": "updaterId",
                "type": "TEXT"
            }
        ],
        "dataset_key": "dataset_6ae53ddc",
        "key_candidates": [
            "id",
            "prjCode",
            "singleProjectCode",
            "prjCode+singleProjectCode"
        ],
        "page_name": "项目前期成果",
        "parent_record_path": "raw_event.sinList[]",
        "partition_field": "prjCode",
        "partition_key": "prjCode",
        "plugin_id": "dcp-dataset-6ae53ddc",
        "record_path": "raw_event.sinList[].sinDateList[]",
        "record_type": "preconstruction_results_detail:raw_event.sinList[].sinDateList[]",
        "table": "canonical_p057_page_6ae53ddc__preconstruction_results_detail__raw_event_sinlist_items_sindatelist_items"
    },
    {
        "api_name": "preconstruction_results_detail",
        "api_path": "/apit/ebuild2-domain-project-form/v1/projectInfoGet/one/queryDetail",
        "columns": [
            {
                "name": "assNum",
                "source": "assNum",
                "type": "TEXT"
            },
            {
                "name": "biddingSectionCode",
                "source": "biddingSectionCode",
                "type": "TEXT"
            },
            {
                "name": "biddingSectionName",
                "source": "biddingSectionName",
                "type": "TEXT"
            },
            {
                "name": "biddingSectionType",
                "source": "biddingSectionType",
                "type": "INTEGER"
            },
            {
                "name": "biddingSectionTypeName",
                "source": "biddingSectionTypeName",
                "type": "TEXT"
            },
            {
                "name": "buildUnitCode",
                "source": "buildUnitCode",
                "type": "TEXT"
            },
            {
                "name": "buildUnitName",
                "source": "buildUnitName",
                "type": "TEXT"
            },
            {
                "name": "constrTransformerCapacity",
                "source": "constrTransformerCapacity",
                "type": "REAL"
            },
            {
                "name": "constructionLineLength",
                "source": "constructionLineLength",
                "type": "TEXT"
            },
            {
                "name": "constructionStatus",
                "source": "constructionStatus",
                "type": "INTEGER"
            },
            {
                "name": "createTime",
                "source": "createTime",
                "type": "TEXT"
            },
            {
                "name": "createType",
                "source": "createType",
                "type": "INTEGER"
            },
            {
                "name": "createrId",
                "source": "createrId",
                "type": "TEXT"
            },
            {
                "name": "deleteFlag",
                "source": "deleteFlag",
                "type": "INTEGER"
            },
            {
                "name": "extra",
                "source": "extra",
                "type": "TEXT"
            },
            {
                "name": "id",
                "source": "id",
                "type": "TEXT"
            },
            {
                "name": "lineQuantity",
                "source": "lineQuantity",
                "type": "TEXT"
            },
            {
                "name": "mainTransformerQuantity",
                "source": "mainTransformerQuantity",
                "type": "TEXT"
            },
            {
                "name": "num",
                "source": "num",
                "type": "TEXT"
            },
            {
                "name": "operationalPermissions",
                "source": "operationalPermissions",
                "type": "TEXT"
            },
            {
                "name": "prjCode",
                "source": "prjCode",
                "type": "TEXT"
            },
            {
                "name": "provinceCode",
                "source": "provinceCode",
                "type": "TEXT"
            },
            {
                "name": "provinceName",
                "source": "provinceName",
                "type": "TEXT"
            },
            {
                "name": "singleLessDTO",
                "source": "singleLessDTO",
                "type": "TEXT"
            },
            {
                "name": "singleProjectCode",
                "source": "singleProjectCode",
                "type": "TEXT"
            },
            {
                "name": "status",
                "source": "status",
                "type": "INTEGER"
            },
            {
                "name": "traceId",
                "source": "traceId",
                "type": "TEXT"
            },
            {
                "name": "updateTime",
                "source": "updateTime",
                "type": "TEXT"
            },
            {
                "name": "updaterId",
                "source": "updaterId",
                "type": "TEXT"
            }
        ],
        "dataset_key": "dataset_6ae53ddc",
        "key_candidates": [
            "id",
            "prjCode",
            "singleProjectCode",
            "biddingSectionCode",
            "prjCode+singleProjectCode+biddingSectionCode"
        ],
        "page_name": "项目前期成果",
        "parent_record_path": "raw_event.sinList[]",
        "partition_field": "prjCode",
        "partition_key": "prjCode",
        "plugin_id": "dcp-dataset-6ae53ddc",
        "record_path": "raw_event.sinList[].bidSectList[]",
        "record_type": "preconstruction_results_detail:raw_event.sinList[].bidSectList[]",
        "table": "canonical_p057_page_6ae53ddc__preconstruction_results_detail__raw_event_sinlist_items_bidsectlist_items"
    },
    {
        "api_name": "preconstruction_results_detail",
        "api_path": "/apit/ebuild2-domain-project-form/v1/projectInfoGet/one/queryDetail",
        "columns": [
            {
                "name": "biddingSectionCode",
                "source": "biddingSectionCode",
                "type": "TEXT"
            },
            {
                "name": "createTime",
                "source": "createTime",
                "type": "TEXT"
            },
            {
                "name": "createrId",
                "source": "createrId",
                "type": "TEXT"
            },
            {
                "name": "deleteFlag",
                "source": "deleteFlag",
                "type": "TEXT"
            },
            {
                "name": "extra",
                "source": "extra",
                "type": "TEXT"
            },
            {
                "name": "id",
                "source": "id",
                "type": "TEXT"
            },
            {
                "name": "prjCode",
                "source": "prjCode",
                "type": "TEXT"
            },
            {
                "name": "singleProjectCode",
                "source": "singleProjectCode",
                "type": "TEXT"
            },
            {
                "name": "taskDate",
                "source": "taskDate",
                "type": "TEXT"
            },
            {
                "name": "taskNameCode",
                "source": "taskNameCode",
                "type": "INTEGER"
            },
            {
                "name": "traceId",
                "source": "traceId",
                "type": "TEXT"
            },
            {
                "name": "updateTime",
                "source": "updateTime",
                "type": "TEXT"
            },
            {
                "name": "updaterId",
                "source": "updaterId",
                "type": "TEXT"
            }
        ],
        "dataset_key": "dataset_6ae53ddc",
        "key_candidates": [
            "id",
            "prjCode",
            "singleProjectCode",
            "biddingSectionCode",
            "prjCode+singleProjectCode+biddingSectionCode"
        ],
        "page_name": "项目前期成果",
        "parent_record_path": "raw_event.sinList[].bidSectList[]",
        "partition_field": "prjCode",
        "partition_key": "prjCode",
        "plugin_id": "dcp-dataset-6ae53ddc",
        "record_path": "raw_event.sinList[].bidSectList[].bidDateList[]",
        "record_type": "preconstruction_results_detail:raw_event.sinList[].bidSectList[].bidDateList[]",
        "table": "canonical_p057_page_6ae53ddc__preconstruction_results_detail__raw_event_sinlist_items_bidsectlist_items_biddat"
    },
    {
        "api_name": "preconstruction_results_detail",
        "api_path": "/apit/ebuild2-domain-project-form/v1/projectInfoGet/one/queryDetail",
        "columns": [
            {
                "name": "createTime",
                "source": "createTime",
                "type": "TEXT"
            },
            {
                "name": "createrId",
                "source": "createrId",
                "type": "TEXT"
            },
            {
                "name": "deleteFlag",
                "source": "deleteFlag",
                "type": "INTEGER"
            },
            {
                "name": "extra",
                "source": "extra",
                "type": "TEXT"
            },
            {
                "name": "id",
                "source": "id",
                "type": "TEXT"
            },
            {
                "name": "prjCode",
                "source": "prjCode",
                "type": "TEXT"
            },
            {
                "name": "taskDate",
                "source": "taskDate",
                "type": "TEXT"
            },
            {
                "name": "taskNameCode",
                "source": "taskNameCode",
                "type": "INTEGER"
            },
            {
                "name": "traceId",
                "source": "traceId",
                "type": "TEXT"
            },
            {
                "name": "updateTime",
                "source": "updateTime",
                "type": "TEXT"
            },
            {
                "name": "updaterId",
                "source": "updaterId",
                "type": "TEXT"
            }
        ],
        "dataset_key": "dataset_6ae53ddc",
        "key_candidates": [
            "id",
            "prjCode"
        ],
        "page_name": "项目前期成果",
        "parent_record_path": "raw_event",
        "partition_field": "prjCode",
        "partition_key": "prjCode",
        "plugin_id": "dcp-dataset-6ae53ddc",
        "record_path": "raw_event.projectDateList[]",
        "record_type": "preconstruction_results_detail:raw_event.projectDateList[]",
        "table": "canonical_p057_page_6ae53ddc__preconstruction_results_detail__raw_event_projectdatelist_items"
    },
    {
        "api_name": "preconstruction_results_detail",
        "api_path": "/apit/ebuild2-domain-project-form/v1/projectInfoGet/queryDetail",
        "columns": [
            {
                "name": "actualCommencementDate",
                "source": "actualCommencementDate",
                "type": "TEXT"
            },
            {
                "name": "actualCommissioningDate",
                "source": "actualCommissioningDate",
                "type": "TEXT"
            },
            {
                "name": "actualComplDate",
                "source": "actualComplDate",
                "type": "TEXT"
            },
            {
                "name": "apprFileNo",
                "source": "apprFileNo",
                "type": "TEXT"
            },
            {
                "name": "buildUnitCode",
                "source": "buildUnitCode",
                "type": "TEXT"
            },
            {
                "name": "buildUnitName",
                "source": "buildUnitName",
                "type": "TEXT"
            },
            {
                "name": "constrAddress",
                "source": "constrAddress",
                "type": "TEXT"
            },
            {
                "name": "constrNature",
                "source": "constrNature",
                "type": "INTEGER"
            },
            {
                "name": "constrNatureName",
                "source": "constrNatureName",
                "type": "TEXT"
            },
            {
                "name": "constrTransformerCapacity",
                "source": "constrTransformerCapacity",
                "type": "REAL"
            },
            {
                "name": "constructionCategory",
                "source": "constructionCategory",
                "type": "INTEGER"
            },
            {
                "name": "constructionCategoryName",
                "source": "constructionCategoryName",
                "type": "TEXT"
            },
            {
                "name": "constructionLineLength",
                "source": "constructionLineLength",
                "type": "TEXT"
            },
            {
                "name": "constructionStatus",
                "source": "constructionStatus",
                "type": "INTEGER"
            },
            {
                "name": "createTime",
                "source": "createTime",
                "type": "TEXT"
            },
            {
                "name": "createrId",
                "source": "createrId",
                "type": "TEXT"
            },
            {
                "name": "deleteButton",
                "source": "deleteButton",
                "type": "TEXT"
            },
            {
                "name": "deleteFlag",
                "source": "deleteFlag",
                "type": "INTEGER"
            },
            {
                "name": "deptStatus",
                "source": "deptStatus",
                "type": "INTEGER"
            },
            {
                "name": "earlierStageFile",
                "source": "earlierStageFile",
                "type": "TEXT"
            },
            {
                "name": "existsFlag",
                "source": "existsFlag",
                "type": "TEXT"
            },
            {
                "name": "extra",
                "source": "extra",
                "type": "TEXT"
            },
            {
                "name": "feaDinvest",
                "source": "feaDinvest",
                "type": "REAL"
            },
            {
                "name": "feaLineLength",
                "source": "feaLineLength",
                "type": "TEXT"
            },
            {
                "name": "feaSinvest",
                "source": "feaSinvest",
                "type": "REAL"
            },
            {
                "name": "feasTransCapacity",
                "source": "feasTransCapacity",
                "type": "REAL"
            },
            {
                "name": "id",
                "source": "id",
                "type": "TEXT"
            },
            {
                "name": "lineQuantity",
                "source": "lineQuantity",
                "type": "TEXT"
            },
            {
                "name": "locationArea",
                "source": "locationArea",
                "type": "TEXT"
            },
            {
                "name": "locationAreaName",
                "source": "locationAreaName",
                "type": "TEXT"
            },
            {
                "name": "locationMunicipality",
                "source": "locationMunicipality",
                "type": "TEXT"
            },
            {
                "name": "locationMunicipalityName",
                "source": "locationMunicipalityName",
                "type": "TEXT"
            },
            {
                "name": "locationProvince",
                "source": "locationProvince",
                "type": "TEXT"
            },
            {
                "name": "locationProvinceName",
                "source": "locationProvinceName",
                "type": "TEXT"
            },
            {
                "name": "mainTransformerQuantity",
                "source": "mainTransformerQuantity",
                "type": "INTEGER"
            },
            {
                "name": "nonConstrDepartmentImpl",
                "source": "nonConstrDepartmentImpl",
                "type": "INTEGER"
            },
            {
                "name": "num",
                "source": "num",
                "type": "TEXT"
            },
            {
                "name": "planComplDate",
                "source": "planComplDate",
                "type": "TEXT"
            },
            {
                "name": "plannedCommencementDate",
                "source": "plannedCommencementDate",
                "type": "TEXT"
            },
            {
                "name": "plannedCommissioningDate",
                "source": "plannedCommissioningDate",
                "type": "TEXT"
            },
            {
                "name": "prjCode",
                "source": "prjCode",
                "type": "TEXT"
            },
            {
                "name": "prjManageMode",
                "source": "prjManageMode",
                "type": "INTEGER"
            },
            {
                "name": "prjName",
                "source": "prjName",
                "type": "TEXT"
            },
            {
                "name": "prjSource",
                "source": "prjSource",
                "type": "INTEGER"
            },
            {
                "name": "prjStatus",
                "source": "prjStatus",
                "type": "TEXT"
            },
            {
                "name": "prodTransCapacity",
                "source": "prodTransCapacity",
                "type": "REAL"
            },
            {
                "name": "productionLineLength",
                "source": "productionLineLength",
                "type": "TEXT"
            },
            {
                "name": "projectApprovalDocumentNo",
                "source": "projectApprovalDocumentNo",
                "type": "TEXT"
            },
            {
                "name": "projectType",
                "source": "projectType",
                "type": "INTEGER"
            },
            {
                "name": "projectTypeName",
                "source": "projectTypeName",
                "type": "TEXT"
            },
            {
                "name": "provinceCode",
                "source": "provinceCode",
                "type": "TEXT"
            },
            {
                "name": "provinceName",
                "source": "provinceName",
                "type": "TEXT"
            },
            {
                "name": "pushStatus",
                "source": "pushStatus",
                "type": "TEXT"
            },
            {
                "name": "reserveButton",
                "source": "reserveButton",
                "type": "INTEGER"
            },
            {
                "name": "same",
                "source": "same",
                "type": "TEXT"
            },
            {
                "name": "sinDivideStatus",
                "source": "sinDivideStatus",
                "type": "TEXT"
            },
            {
                "name": "traceId",
                "source": "traceId",
                "type": "TEXT"
            },
            {
                "name": "updateTime",
                "source": "updateTime",
                "type": "TEXT"
            },
            {
                "name": "updaterId",
                "source": "updaterId",
                "type": "TEXT"
            },
            {
                "name": "voltageLevel",
                "source": "voltageLevel",
                "type": "TEXT"
            },
            {
                "name": "voltageLevelName",
                "source": "voltageLevelName",
                "type": "TEXT"
            }
        ],
        "dataset_key": "dataset_de3264f2",
        "key_candidates": [
            "id",
            "prjCode"
        ],
        "page_name": "项目基本信息",
        "parent_record_path": null,
        "partition_field": "prjCode",
        "partition_key": "prjCode",
        "plugin_id": "dcp-dataset-de3264f2",
        "record_path": "raw_event",
        "record_type": "preconstruction_results_detail:raw_event",
        "table": "canonical_p058_page_de3264f2__preconstruction_results_detail__raw_event"
    },
    {
        "api_name": "preconstruction_results_detail",
        "api_path": "/apit/ebuild2-domain-project-form/v1/projectInfoGet/queryDetail",
        "columns": [
            {
                "name": "actualCommencementDate",
                "source": "actualCommencementDate",
                "type": "TEXT"
            },
            {
                "name": "actualCommissioningDate",
                "source": "actualCommissioningDate",
                "type": "TEXT"
            },
            {
                "name": "actualCompletionDate",
                "source": "actualCompletionDate",
                "type": "TEXT"
            },
            {
                "name": "buildUnitCode",
                "source": "buildUnitCode",
                "type": "TEXT"
            },
            {
                "name": "buildUnitName",
                "source": "buildUnitName",
                "type": "TEXT"
            },
            {
                "name": "commencementOrderCount",
                "source": "commencementOrderCount",
                "type": "INTEGER"
            },
            {
                "name": "constrAddress",
                "source": "constrAddress",
                "type": "TEXT"
            },
            {
                "name": "constrNature",
                "source": "constrNature",
                "type": "INTEGER"
            },
            {
                "name": "constrNatureName",
                "source": "constrNatureName",
                "type": "TEXT"
            },
            {
                "name": "constrTransformerCapacity",
                "source": "constrTransformerCapacity",
                "type": "REAL"
            },
            {
                "name": "constructionLineLength",
                "source": "constructionLineLength",
                "type": "TEXT"
            },
            {
                "name": "constructionStatus",
                "source": "constructionStatus",
                "type": "INTEGER"
            },
            {
                "name": "createTime",
                "source": "createTime",
                "type": "TEXT"
            },
            {
                "name": "createrId",
                "source": "createrId",
                "type": "TEXT"
            },
            {
                "name": "deleteFlag",
                "source": "deleteFlag",
                "type": "INTEGER"
            },
            {
                "name": "extra",
                "source": "extra",
                "type": "TEXT"
            },
            {
                "name": "feaDinvest",
                "source": "feaDinvest",
                "type": "REAL"
            },
            {
                "name": "feaLineLength",
                "source": "feaLineLength",
                "type": "TEXT"
            },
            {
                "name": "feaSinvest",
                "source": "feaSinvest",
                "type": "REAL"
            },
            {
                "name": "feasTransCapacity",
                "source": "feasTransCapacity",
                "type": "TEXT"
            },
            {
                "name": "id",
                "source": "id",
                "type": "TEXT"
            },
            {
                "name": "integrateIntosysFlag",
                "source": "integrateIntosysFlag",
                "type": "INTEGER"
            },
            {
                "name": "itemId",
                "source": "itemId",
                "type": "TEXT"
            },
            {
                "name": "kfDeleteFlag",
                "source": "kfDeleteFlag",
                "type": "INTEGER"
            },
            {
                "name": "lineQuantity",
                "source": "lineQuantity",
                "type": "TEXT"
            },
            {
                "name": "locationArea",
                "source": "locationArea",
                "type": "TEXT"
            },
            {
                "name": "locationAreaName",
                "source": "locationAreaName",
                "type": "TEXT"
            },
            {
                "name": "locationMunicipality",
                "source": "locationMunicipality",
                "type": "TEXT"
            },
            {
                "name": "locationMunicipalityName",
                "source": "locationMunicipalityName",
                "type": "TEXT"
            },
            {
                "name": "locationProvince",
                "source": "locationProvince",
                "type": "TEXT"
            },
            {
                "name": "locationProvinceName",
                "source": "locationProvinceName",
                "type": "TEXT"
            },
            {
                "name": "mainTransformerQuantity",
                "source": "mainTransformerQuantity",
                "type": "INTEGER"
            },
            {
                "name": "num",
                "source": "num",
                "type": "TEXT"
            },
            {
                "name": "operationalPermissions",
                "source": "operationalPermissions",
                "type": "TEXT"
            },
            {
                "name": "parentItemId",
                "source": "parentItemId",
                "type": "TEXT"
            },
            {
                "name": "planComplDate",
                "source": "planComplDate",
                "type": "TEXT"
            },
            {
                "name": "plannedCommencementDate",
                "source": "plannedCommencementDate",
                "type": "TEXT"
            },
            {
                "name": "plannedCommissioningDate",
                "source": "plannedCommissioningDate",
                "type": "TEXT"
            },
            {
                "name": "prjCode",
                "source": "prjCode",
                "type": "TEXT"
            },
            {
                "name": "prjStatus",
                "source": "prjStatus",
                "type": "TEXT"
            },
            {
                "name": "prodTransCapacity",
                "source": "prodTransCapacity",
                "type": "REAL"
            },
            {
                "name": "productionLineLength",
                "source": "productionLineLength",
                "type": "TEXT"
            },
            {
                "name": "provinceCode",
                "source": "provinceCode",
                "type": "TEXT"
            },
            {
                "name": "provinceName",
                "source": "provinceName",
                "type": "TEXT"
            },
            {
                "name": "revokeStatus",
                "source": "revokeStatus",
                "type": "TEXT"
            },
            {
                "name": "sinProgress",
                "source": "sinProgress",
                "type": "TEXT"
            },
            {
                "name": "singleProjectCode",
                "source": "singleProjectCode",
                "type": "TEXT"
            },
            {
                "name": "singleProjectDetailsType",
                "source": "singleProjectDetailsType",
                "type": "INTEGER"
            },
            {
                "name": "singleProjectDetailsTypeName",
                "source": "singleProjectDetailsTypeName",
                "type": "TEXT"
            },
            {
                "name": "singleProjectName",
                "source": "singleProjectName",
                "type": "TEXT"
            },
            {
                "name": "singleProjectPrerType",
                "source": "singleProjectPrerType",
                "type": "TEXT"
            },
            {
                "name": "singleProjectPrerTypeName",
                "source": "singleProjectPrerTypeName",
                "type": "TEXT"
            },
            {
                "name": "singleProjectType",
                "source": "singleProjectType",
                "type": "INTEGER"
            },
            {
                "name": "singleProjectTypeName",
                "source": "singleProjectTypeName",
                "type": "TEXT"
            },
            {
                "name": "status",
                "source": "status",
                "type": "INTEGER"
            },
            {
                "name": "traceId",
                "source": "traceId",
                "type": "TEXT"
            },
            {
                "name": "updateTime",
                "source": "updateTime",
                "type": "TEXT"
            },
            {
                "name": "updaterId",
                "source": "updaterId",
                "type": "TEXT"
            },
            {
                "name": "voltageLevel",
                "source": "voltageLevel",
                "type": "TEXT"
            },
            {
                "name": "voltageLevelName",
                "source": "voltageLevelName",
                "type": "TEXT"
            }
        ],
        "dataset_key": "dataset_de3264f2",
        "key_candidates": [
            "id",
            "prjCode",
            "singleProjectCode",
            "prjCode+singleProjectCode"
        ],
        "page_name": "项目基本信息",
        "parent_record_path": "raw_event",
        "partition_field": "prjCode",
        "partition_key": "prjCode",
        "plugin_id": "dcp-dataset-de3264f2",
        "record_path": "raw_event.sinList[]",
        "record_type": "preconstruction_results_detail:raw_event.sinList[]",
        "table": "canonical_p058_page_de3264f2__preconstruction_results_detail__raw_event_sinlist_items"
    },
    {
        "api_name": "preconstruction_results_detail",
        "api_path": "/apit/ebuild2-domain-project-form/v1/projectInfoGet/queryDetail",
        "columns": [
            {
                "name": "createTime",
                "source": "createTime",
                "type": "TEXT"
            },
            {
                "name": "createrId",
                "source": "createrId",
                "type": "TEXT"
            },
            {
                "name": "deleteFlag",
                "source": "deleteFlag",
                "type": "INTEGER"
            },
            {
                "name": "extra",
                "source": "extra",
                "type": "TEXT"
            },
            {
                "name": "id",
                "source": "id",
                "type": "TEXT"
            },
            {
                "name": "prjCode",
                "source": "prjCode",
                "type": "TEXT"
            },
            {
                "name": "singleProjectCode",
                "source": "singleProjectCode",
                "type": "TEXT"
            },
            {
                "name": "taskDate",
                "source": "taskDate",
                "type": "TEXT"
            },
            {
                "name": "taskNameCode",
                "source": "taskNameCode",
                "type": "INTEGER"
            },
            {
                "name": "traceId",
                "source": "traceId",
                "type": "TEXT"
            },
            {
                "name": "updateTime",
                "source": "updateTime",
                "type": "TEXT"
            },
            {
                "name": "updaterId",
                "source": "updaterId",
                "type": "TEXT"
            }
        ],
        "dataset_key": "dataset_de3264f2",
        "key_candidates": [
            "id",
            "prjCode",
            "singleProjectCode",
            "prjCode+singleProjectCode"
        ],
        "page_name": "项目基本信息",
        "parent_record_path": "raw_event.sinList[]",
        "partition_field": "prjCode",
        "partition_key": "prjCode",
        "plugin_id": "dcp-dataset-de3264f2",
        "record_path": "raw_event.sinList[].sinDateList[]",
        "record_type": "preconstruction_results_detail:raw_event.sinList[].sinDateList[]",
        "table": "canonical_p058_page_de3264f2__preconstruction_results_detail__raw_event_sinlist_items_sindatelist_items"
    },
    {
        "api_name": "preconstruction_results_detail",
        "api_path": "/apit/ebuild2-domain-project-form/v1/projectInfoGet/queryDetail",
        "columns": [
            {
                "name": "assNum",
                "source": "assNum",
                "type": "TEXT"
            },
            {
                "name": "biddingSectionCode",
                "source": "biddingSectionCode",
                "type": "TEXT"
            },
            {
                "name": "biddingSectionName",
                "source": "biddingSectionName",
                "type": "TEXT"
            },
            {
                "name": "biddingSectionType",
                "source": "biddingSectionType",
                "type": "INTEGER"
            },
            {
                "name": "biddingSectionTypeName",
                "source": "biddingSectionTypeName",
                "type": "TEXT"
            },
            {
                "name": "buildUnitCode",
                "source": "buildUnitCode",
                "type": "TEXT"
            },
            {
                "name": "buildUnitName",
                "source": "buildUnitName",
                "type": "TEXT"
            },
            {
                "name": "constrTransformerCapacity",
                "source": "constrTransformerCapacity",
                "type": "REAL"
            },
            {
                "name": "constructionLineLength",
                "source": "constructionLineLength",
                "type": "TEXT"
            },
            {
                "name": "constructionStatus",
                "source": "constructionStatus",
                "type": "INTEGER"
            },
            {
                "name": "createTime",
                "source": "createTime",
                "type": "TEXT"
            },
            {
                "name": "createType",
                "source": "createType",
                "type": "INTEGER"
            },
            {
                "name": "createrId",
                "source": "createrId",
                "type": "TEXT"
            },
            {
                "name": "deleteFlag",
                "source": "deleteFlag",
                "type": "INTEGER"
            },
            {
                "name": "extra",
                "source": "extra",
                "type": "TEXT"
            },
            {
                "name": "id",
                "source": "id",
                "type": "TEXT"
            },
            {
                "name": "lineQuantity",
                "source": "lineQuantity",
                "type": "TEXT"
            },
            {
                "name": "mainTransformerQuantity",
                "source": "mainTransformerQuantity",
                "type": "TEXT"
            },
            {
                "name": "num",
                "source": "num",
                "type": "TEXT"
            },
            {
                "name": "operationalPermissions",
                "source": "operationalPermissions",
                "type": "TEXT"
            },
            {
                "name": "prjCode",
                "source": "prjCode",
                "type": "TEXT"
            },
            {
                "name": "provinceCode",
                "source": "provinceCode",
                "type": "TEXT"
            },
            {
                "name": "provinceName",
                "source": "provinceName",
                "type": "TEXT"
            },
            {
                "name": "singleLessDTO",
                "source": "singleLessDTO",
                "type": "TEXT"
            },
            {
                "name": "singleProjectCode",
                "source": "singleProjectCode",
                "type": "TEXT"
            },
            {
                "name": "status",
                "source": "status",
                "type": "INTEGER"
            },
            {
                "name": "traceId",
                "source": "traceId",
                "type": "TEXT"
            },
            {
                "name": "updateTime",
                "source": "updateTime",
                "type": "TEXT"
            },
            {
                "name": "updaterId",
                "source": "updaterId",
                "type": "TEXT"
            }
        ],
        "dataset_key": "dataset_de3264f2",
        "key_candidates": [
            "id",
            "prjCode",
            "singleProjectCode",
            "biddingSectionCode",
            "prjCode+singleProjectCode+biddingSectionCode"
        ],
        "page_name": "项目基本信息",
        "parent_record_path": "raw_event.sinList[]",
        "partition_field": "prjCode",
        "partition_key": "prjCode",
        "plugin_id": "dcp-dataset-de3264f2",
        "record_path": "raw_event.sinList[].bidSectList[]",
        "record_type": "preconstruction_results_detail:raw_event.sinList[].bidSectList[]",
        "table": "canonical_p058_page_de3264f2__preconstruction_results_detail__raw_event_sinlist_items_bidsectlist_items"
    },
    {
        "api_name": "preconstruction_results_detail",
        "api_path": "/apit/ebuild2-domain-project-form/v1/projectInfoGet/queryDetail",
        "columns": [
            {
                "name": "biddingSectionCode",
                "source": "biddingSectionCode",
                "type": "TEXT"
            },
            {
                "name": "createTime",
                "source": "createTime",
                "type": "TEXT"
            },
            {
                "name": "createrId",
                "source": "createrId",
                "type": "TEXT"
            },
            {
                "name": "deleteFlag",
                "source": "deleteFlag",
                "type": "TEXT"
            },
            {
                "name": "extra",
                "source": "extra",
                "type": "TEXT"
            },
            {
                "name": "id",
                "source": "id",
                "type": "TEXT"
            },
            {
                "name": "prjCode",
                "source": "prjCode",
                "type": "TEXT"
            },
            {
                "name": "singleProjectCode",
                "source": "singleProjectCode",
                "type": "TEXT"
            },
            {
                "name": "taskDate",
                "source": "taskDate",
                "type": "TEXT"
            },
            {
                "name": "taskNameCode",
                "source": "taskNameCode",
                "type": "INTEGER"
            },
            {
                "name": "traceId",
                "source": "traceId",
                "type": "TEXT"
            },
            {
                "name": "updateTime",
                "source": "updateTime",
                "type": "TEXT"
            },
            {
                "name": "updaterId",
                "source": "updaterId",
                "type": "TEXT"
            }
        ],
        "dataset_key": "dataset_de3264f2",
        "key_candidates": [
            "id",
            "prjCode",
            "singleProjectCode",
            "biddingSectionCode",
            "prjCode+singleProjectCode+biddingSectionCode"
        ],
        "page_name": "项目基本信息",
        "parent_record_path": "raw_event.sinList[].bidSectList[]",
        "partition_field": "prjCode",
        "partition_key": "prjCode",
        "plugin_id": "dcp-dataset-de3264f2",
        "record_path": "raw_event.sinList[].bidSectList[].bidDateList[]",
        "record_type": "preconstruction_results_detail:raw_event.sinList[].bidSectList[].bidDateList[]",
        "table": "canonical_p058_page_de3264f2__preconstruction_results_detail__raw_event_sinlist_items_bidsectlist_items_biddat"
    },
    {
        "api_name": "preconstruction_results_detail",
        "api_path": "/apit/ebuild2-domain-project-form/v1/projectInfoGet/queryDetail",
        "columns": [
            {
                "name": "createTime",
                "source": "createTime",
                "type": "TEXT"
            },
            {
                "name": "createrId",
                "source": "createrId",
                "type": "TEXT"
            },
            {
                "name": "deleteFlag",
                "source": "deleteFlag",
                "type": "INTEGER"
            },
            {
                "name": "extra",
                "source": "extra",
                "type": "TEXT"
            },
            {
                "name": "id",
                "source": "id",
                "type": "TEXT"
            },
            {
                "name": "prjCode",
                "source": "prjCode",
                "type": "TEXT"
            },
            {
                "name": "taskDate",
                "source": "taskDate",
                "type": "TEXT"
            },
            {
                "name": "taskNameCode",
                "source": "taskNameCode",
                "type": "INTEGER"
            },
            {
                "name": "traceId",
                "source": "traceId",
                "type": "TEXT"
            },
            {
                "name": "updateTime",
                "source": "updateTime",
                "type": "TEXT"
            },
            {
                "name": "updaterId",
                "source": "updaterId",
                "type": "TEXT"
            }
        ],
        "dataset_key": "dataset_de3264f2",
        "key_candidates": [
            "id",
            "prjCode"
        ],
        "page_name": "项目基本信息",
        "parent_record_path": "raw_event",
        "partition_field": "prjCode",
        "partition_key": "prjCode",
        "plugin_id": "dcp-dataset-de3264f2",
        "record_path": "raw_event.projectDateList[]",
        "record_type": "preconstruction_results_detail:raw_event.projectDateList[]",
        "table": "canonical_p058_page_de3264f2__preconstruction_results_detail__raw_event_projectdatelist_items"
    },
    {
        "api_name": "implementation_plan",
        "api_path": "/apit/ebuild2-domain-project-stage/v1/implPlan/queryImplNodes",
        "columns": [
            {
                "name": "adjustedPlannedEndDate",
                "source": "adjustedPlannedEndDate",
                "type": "TEXT"
            },
            {
                "name": "adjustedPlannedStartDate",
                "source": "adjustedPlannedStartDate",
                "type": "TEXT"
            },
            {
                "name": "biddingSectionCode",
                "source": "biddingSectionCode",
                "type": "TEXT"
            },
            {
                "name": "deleteFlag",
                "source": "deleteFlag",
                "type": "TEXT"
            },
            {
                "name": "extra",
                "source": "extra",
                "type": "TEXT"
            },
            {
                "name": "id",
                "source": "id",
                "type": "TEXT"
            },
            {
                "name": "involveFlag",
                "source": "involveFlag",
                "type": "INTEGER"
            },
            {
                "name": "involveFlagBefore",
                "source": "involveFlagBefore",
                "type": "INTEGER"
            },
            {
                "name": "jobContent",
                "source": "jobContent",
                "type": "TEXT"
            },
            {
                "name": "keyPath",
                "source": "keyPath",
                "type": "TEXT"
            },
            {
                "name": "nodeId",
                "source": "nodeId",
                "type": "TEXT"
            },
            {
                "name": "nodeType",
                "source": "nodeType",
                "type": "INTEGER"
            },
            {
                "name": "planId",
                "source": "planId",
                "type": "TEXT"
            },
            {
                "name": "plannedEndDate",
                "source": "plannedEndDate",
                "type": "TEXT"
            },
            {
                "name": "plannedStartDate",
                "source": "plannedStartDate",
                "type": "TEXT"
            },
            {
                "name": "prjCode",
                "source": "prjCode",
                "type": "TEXT"
            },
            {
                "name": "remark",
                "source": "remark",
                "type": "TEXT"
            },
            {
                "name": "singleProjectCode",
                "source": "singleProjectCode",
                "type": "TEXT"
            },
            {
                "name": "singleProjectType",
                "source": "singleProjectType",
                "type": "INTEGER"
            },
            {
                "name": "sourceDescription",
                "source": "sourceDescription",
                "type": "TEXT"
            },
            {
                "name": "traceId",
                "source": "traceId",
                "type": "TEXT"
            },
            {
                "name": "workflowId",
                "source": "workflowId",
                "type": "TEXT"
            }
        ],
        "dataset_key": "dataset_f313e3e9",
        "key_candidates": [
            "id",
            "prjCode",
            "singleProjectCode",
            "biddingSectionCode",
            "prjCode+singleProjectCode+biddingSectionCode"
        ],
        "page_name": "项目实施计划",
        "parent_record_path": null,
        "partition_field": "prjCode",
        "partition_key": "prjCode",
        "plugin_id": "dcp-dataset-f313e3e9",
        "record_path": "raw_event",
        "record_type": "implementation_plan:raw_event",
        "table": "canonical_p059_page_f313e3e9__implementation_plan__raw_event"
    },
    {
        "api_name": "project_management",
        "api_path": "/apit/ebuild2-domain-project-form/v1/projectInfoGet/queryList",
        "columns": [
            {
                "name": "actualCommencementDate",
                "source": "actualCommencementDate",
                "type": "TEXT"
            },
            {
                "name": "actualCommissioningDate",
                "source": "actualCommissioningDate",
                "type": "TEXT"
            },
            {
                "name": "actualComplDate",
                "source": "actualComplDate",
                "type": "TEXT"
            },
            {
                "name": "apprFileNo",
                "source": "apprFileNo",
                "type": "TEXT"
            },
            {
                "name": "buildUnitCode",
                "source": "buildUnitCode",
                "type": "TEXT"
            },
            {
                "name": "buildUnitName",
                "source": "buildUnitName",
                "type": "TEXT"
            },
            {
                "name": "constrAddress",
                "source": "constrAddress",
                "type": "TEXT"
            },
            {
                "name": "constrNature",
                "source": "constrNature",
                "type": "INTEGER"
            },
            {
                "name": "constrNatureName",
                "source": "constrNatureName",
                "type": "TEXT"
            },
            {
                "name": "constrTransformerCapacity",
                "source": "constrTransformerCapacity",
                "type": "REAL"
            },
            {
                "name": "constructionCategory",
                "source": "constructionCategory",
                "type": "INTEGER"
            },
            {
                "name": "constructionCategoryName",
                "source": "constructionCategoryName",
                "type": "TEXT"
            },
            {
                "name": "constructionLineLength",
                "source": "constructionLineLength",
                "type": "REAL"
            },
            {
                "name": "constructionStatus",
                "source": "constructionStatus",
                "type": "INTEGER"
            },
            {
                "name": "createTime",
                "source": "createTime",
                "type": "TEXT"
            },
            {
                "name": "createrId",
                "source": "createrId",
                "type": "TEXT"
            },
            {
                "name": "deleteButton",
                "source": "deleteButton",
                "type": "INTEGER"
            },
            {
                "name": "deleteFlag",
                "source": "deleteFlag",
                "type": "INTEGER"
            },
            {
                "name": "deptStatus",
                "source": "deptStatus",
                "type": "TEXT"
            },
            {
                "name": "earlierStageFile",
                "source": "earlierStageFile",
                "type": "TEXT"
            },
            {
                "name": "existsFlag",
                "source": "existsFlag",
                "type": "TEXT"
            },
            {
                "name": "extra",
                "source": "extra",
                "type": "TEXT"
            },
            {
                "name": "feaDinvest",
                "source": "feaDinvest",
                "type": "REAL"
            },
            {
                "name": "feaLineLength",
                "source": "feaLineLength",
                "type": "REAL"
            },
            {
                "name": "feaSinvest",
                "source": "feaSinvest",
                "type": "REAL"
            },
            {
                "name": "feasTransCapacity",
                "source": "feasTransCapacity",
                "type": "REAL"
            },
            {
                "name": "id",
                "source": "id",
                "type": "TEXT"
            },
            {
                "name": "lineQuantity",
                "source": "lineQuantity",
                "type": "INTEGER"
            },
            {
                "name": "locationArea",
                "source": "locationArea",
                "type": "TEXT"
            },
            {
                "name": "locationAreaName",
                "source": "locationAreaName",
                "type": "TEXT"
            },
            {
                "name": "locationMunicipality",
                "source": "locationMunicipality",
                "type": "TEXT"
            },
            {
                "name": "locationMunicipalityName",
                "source": "locationMunicipalityName",
                "type": "TEXT"
            },
            {
                "name": "locationProvince",
                "source": "locationProvince",
                "type": "TEXT"
            },
            {
                "name": "locationProvinceName",
                "source": "locationProvinceName",
                "type": "TEXT"
            },
            {
                "name": "mainTransformerQuantity",
                "source": "mainTransformerQuantity",
                "type": "INTEGER"
            },
            {
                "name": "nonConstrDepartmentImpl",
                "source": "nonConstrDepartmentImpl",
                "type": "INTEGER"
            },
            {
                "name": "num",
                "source": "num",
                "type": "TEXT"
            },
            {
                "name": "planComplDate",
                "source": "planComplDate",
                "type": "TEXT"
            },
            {
                "name": "plannedCommencementDate",
                "source": "plannedCommencementDate",
                "type": "TEXT"
            },
            {
                "name": "plannedCommissioningDate",
                "source": "plannedCommissioningDate",
                "type": "TEXT"
            },
            {
                "name": "prjCode",
                "source": "prjCode",
                "type": "TEXT"
            },
            {
                "name": "prjManageMode",
                "source": "prjManageMode",
                "type": "INTEGER"
            },
            {
                "name": "prjName",
                "source": "prjName",
                "type": "TEXT"
            },
            {
                "name": "prjSource",
                "source": "prjSource",
                "type": "INTEGER"
            },
            {
                "name": "prjStatus",
                "source": "prjStatus",
                "type": "INTEGER"
            },
            {
                "name": "prodTransCapacity",
                "source": "prodTransCapacity",
                "type": "TEXT"
            },
            {
                "name": "productionLineLength",
                "source": "productionLineLength",
                "type": "TEXT"
            },
            {
                "name": "projectApprovalDocumentNo",
                "source": "projectApprovalDocumentNo",
                "type": "TEXT"
            },
            {
                "name": "projectType",
                "source": "projectType",
                "type": "INTEGER"
            },
            {
                "name": "projectTypeName",
                "source": "projectTypeName",
                "type": "TEXT"
            },
            {
                "name": "provinceCode",
                "source": "provinceCode",
                "type": "TEXT"
            },
            {
                "name": "provinceName",
                "source": "provinceName",
                "type": "TEXT"
            },
            {
                "name": "pushStatus",
                "source": "pushStatus",
                "type": "TEXT"
            },
            {
                "name": "reserveButton",
                "source": "reserveButton",
                "type": "INTEGER"
            },
            {
                "name": "same",
                "source": "same",
                "type": "INTEGER"
            },
            {
                "name": "sinDivideStatus",
                "source": "sinDivideStatus",
                "type": "TEXT"
            },
            {
                "name": "sinList",
                "source": "sinList",
                "type": "TEXT"
            },
            {
                "name": "traceId",
                "source": "traceId",
                "type": "TEXT"
            },
            {
                "name": "updateTime",
                "source": "updateTime",
                "type": "TEXT"
            },
            {
                "name": "updaterId",
                "source": "updaterId",
                "type": "TEXT"
            },
            {
                "name": "voltageLevel",
                "source": "voltageLevel",
                "type": "TEXT"
            },
            {
                "name": "voltageLevelName",
                "source": "voltageLevelName",
                "type": "TEXT"
            }
        ],
        "dataset_key": "dataset_4f9a248d",
        "key_candidates": [
            "id",
            "prjCode"
        ],
        "page_name": "项目管理",
        "parent_record_path": null,
        "partition_field": "prjCode",
        "partition_key": "prjCode",
        "plugin_id": "dcp-dataset-4f9a248d",
        "record_path": "raw_event",
        "record_type": "project_management:raw_event",
        "table": "canonical_p060_page_4f9a248d__project_management__raw_event"
    },
    {
        "api_name": "project_management",
        "api_path": "/apit/ebuild2-domain-project-form/v1/projectInfoGet/queryList",
        "columns": [
            {
                "name": "createTime",
                "source": "createTime",
                "type": "TEXT"
            },
            {
                "name": "createrId",
                "source": "createrId",
                "type": "TEXT"
            },
            {
                "name": "deleteFlag",
                "source": "deleteFlag",
                "type": "INTEGER"
            },
            {
                "name": "extra",
                "source": "extra",
                "type": "TEXT"
            },
            {
                "name": "id",
                "source": "id",
                "type": "TEXT"
            },
            {
                "name": "prjCode",
                "source": "prjCode",
                "type": "TEXT"
            },
            {
                "name": "taskDate",
                "source": "taskDate",
                "type": "TEXT"
            },
            {
                "name": "taskNameCode",
                "source": "taskNameCode",
                "type": "INTEGER"
            },
            {
                "name": "traceId",
                "source": "traceId",
                "type": "TEXT"
            },
            {
                "name": "updateTime",
                "source": "updateTime",
                "type": "TEXT"
            },
            {
                "name": "updaterId",
                "source": "updaterId",
                "type": "TEXT"
            }
        ],
        "dataset_key": "dataset_4f9a248d",
        "key_candidates": [
            "id",
            "prjCode"
        ],
        "page_name": "项目管理",
        "parent_record_path": "raw_event",
        "partition_field": "prjCode",
        "partition_key": "prjCode",
        "plugin_id": "dcp-dataset-4f9a248d",
        "record_path": "raw_event.projectDateList[]",
        "record_type": "project_management:raw_event.projectDateList[]",
        "table": "canonical_p060_page_4f9a248d__project_management__raw_event_projectdatelist_items"
    },
    {
        "api_name": "project_management",
        "api_path": "/apit/ebuild2-domain-project-form/v1/projectInfoGet/queryList",
        "columns": [
            {
                "name": "actualCommencementDate",
                "source": "actualCommencementDate",
                "type": "TEXT"
            },
            {
                "name": "actualCommissioningDate",
                "source": "actualCommissioningDate",
                "type": "TEXT"
            },
            {
                "name": "actualCompletionDate",
                "source": "actualCompletionDate",
                "type": "TEXT"
            },
            {
                "name": "bidSectList",
                "source": "bidSectList",
                "type": "TEXT"
            },
            {
                "name": "buildUnitCode",
                "source": "buildUnitCode",
                "type": "TEXT"
            },
            {
                "name": "buildUnitName",
                "source": "buildUnitName",
                "type": "TEXT"
            },
            {
                "name": "commencementOrderCount",
                "source": "commencementOrderCount",
                "type": "INTEGER"
            },
            {
                "name": "constrAddress",
                "source": "constrAddress",
                "type": "TEXT"
            },
            {
                "name": "constrNature",
                "source": "constrNature",
                "type": "INTEGER"
            },
            {
                "name": "constrNatureName",
                "source": "constrNatureName",
                "type": "TEXT"
            },
            {
                "name": "constrTransformerCapacity",
                "source": "constrTransformerCapacity",
                "type": "REAL"
            },
            {
                "name": "constructionLineLength",
                "source": "constructionLineLength",
                "type": "REAL"
            },
            {
                "name": "constructionStatus",
                "source": "constructionStatus",
                "type": "INTEGER"
            },
            {
                "name": "createTime",
                "source": "createTime",
                "type": "TEXT"
            },
            {
                "name": "createrId",
                "source": "createrId",
                "type": "TEXT"
            },
            {
                "name": "deleteFlag",
                "source": "deleteFlag",
                "type": "INTEGER"
            },
            {
                "name": "extra",
                "source": "extra",
                "type": "TEXT"
            },
            {
                "name": "feaDinvest",
                "source": "feaDinvest",
                "type": "REAL"
            },
            {
                "name": "feaLineLength",
                "source": "feaLineLength",
                "type": "TEXT"
            },
            {
                "name": "feaSinvest",
                "source": "feaSinvest",
                "type": "REAL"
            },
            {
                "name": "feasTransCapacity",
                "source": "feasTransCapacity",
                "type": "TEXT"
            },
            {
                "name": "id",
                "source": "id",
                "type": "TEXT"
            },
            {
                "name": "integrateIntosysFlag",
                "source": "integrateIntosysFlag",
                "type": "INTEGER"
            },
            {
                "name": "itemId",
                "source": "itemId",
                "type": "TEXT"
            },
            {
                "name": "kfDeleteFlag",
                "source": "kfDeleteFlag",
                "type": "INTEGER"
            },
            {
                "name": "lineQuantity",
                "source": "lineQuantity",
                "type": "INTEGER"
            },
            {
                "name": "locationArea",
                "source": "locationArea",
                "type": "TEXT"
            },
            {
                "name": "locationAreaName",
                "source": "locationAreaName",
                "type": "TEXT"
            },
            {
                "name": "locationMunicipality",
                "source": "locationMunicipality",
                "type": "TEXT"
            },
            {
                "name": "locationMunicipalityName",
                "source": "locationMunicipalityName",
                "type": "TEXT"
            },
            {
                "name": "locationProvince",
                "source": "locationProvince",
                "type": "TEXT"
            },
            {
                "name": "locationProvinceName",
                "source": "locationProvinceName",
                "type": "TEXT"
            },
            {
                "name": "mainTransformerQuantity",
                "source": "mainTransformerQuantity",
                "type": "INTEGER"
            },
            {
                "name": "num",
                "source": "num",
                "type": "TEXT"
            },
            {
                "name": "operationalPermissions",
                "source": "operationalPermissions",
                "type": "TEXT"
            },
            {
                "name": "parentItemId",
                "source": "parentItemId",
                "type": "TEXT"
            },
            {
                "name": "planComplDate",
                "source": "planComplDate",
                "type": "TEXT"
            },
            {
                "name": "plannedCommencementDate",
                "source": "plannedCommencementDate",
                "type": "TEXT"
            },
            {
                "name": "plannedCommissioningDate",
                "source": "plannedCommissioningDate",
                "type": "TEXT"
            },
            {
                "name": "prjCode",
                "source": "prjCode",
                "type": "TEXT"
            },
            {
                "name": "prjStatus",
                "source": "prjStatus",
                "type": "TEXT"
            },
            {
                "name": "prodTransCapacity",
                "source": "prodTransCapacity",
                "type": "TEXT"
            },
            {
                "name": "productionLineLength",
                "source": "productionLineLength",
                "type": "TEXT"
            },
            {
                "name": "provinceCode",
                "source": "provinceCode",
                "type": "TEXT"
            },
            {
                "name": "provinceName",
                "source": "provinceName",
                "type": "TEXT"
            },
            {
                "name": "revokeStatus",
                "source": "revokeStatus",
                "type": "TEXT"
            },
            {
                "name": "sinDateList",
                "source": "sinDateList",
                "type": "TEXT"
            },
            {
                "name": "sinProgress",
                "source": "sinProgress",
                "type": "TEXT"
            },
            {
                "name": "singleProjectCode",
                "source": "singleProjectCode",
                "type": "TEXT"
            },
            {
                "name": "singleProjectDetailsType",
                "source": "singleProjectDetailsType",
                "type": "INTEGER"
            },
            {
                "name": "singleProjectDetailsTypeName",
                "source": "singleProjectDetailsTypeName",
                "type": "TEXT"
            },
            {
                "name": "singleProjectName",
                "source": "singleProjectName",
                "type": "TEXT"
            },
            {
                "name": "singleProjectPrerType",
                "source": "singleProjectPrerType",
                "type": "TEXT"
            },
            {
                "name": "singleProjectPrerTypeName",
                "source": "singleProjectPrerTypeName",
                "type": "TEXT"
            },
            {
                "name": "singleProjectType",
                "source": "singleProjectType",
                "type": "INTEGER"
            },
            {
                "name": "singleProjectTypeName",
                "source": "singleProjectTypeName",
                "type": "TEXT"
            },
            {
                "name": "status",
                "source": "status",
                "type": "INTEGER"
            },
            {
                "name": "traceId",
                "source": "traceId",
                "type": "TEXT"
            },
            {
                "name": "updateTime",
                "source": "updateTime",
                "type": "TEXT"
            },
            {
                "name": "updaterId",
                "source": "updaterId",
                "type": "TEXT"
            },
            {
                "name": "voltageLevel",
                "source": "voltageLevel",
                "type": "TEXT"
            },
            {
                "name": "voltageLevelName",
                "source": "voltageLevelName",
                "type": "TEXT"
            }
        ],
        "dataset_key": "dataset_4f9a248d",
        "key_candidates": [
            "id",
            "prjCode",
            "singleProjectCode",
            "prjCode+singleProjectCode"
        ],
        "page_name": "项目管理",
        "parent_record_path": "raw_event",
        "partition_field": "prjCode",
        "partition_key": "prjCode",
        "plugin_id": "dcp-dataset-4f9a248d",
        "record_path": "raw_event.sinList[]",
        "record_type": "project_management:raw_event.sinList[]",
        "table": "canonical_p060_page_4f9a248d__project_management__raw_event_sinlist_items"
    },
    {
        "api_name": "construction_outline",
        "api_path": "/apit/ebuild2-domain-project-stage/v1/implementPlanning/queryImplementPlanningPage",
        "columns": [
            {
                "name": "approvalStatus",
                "source": "approvalStatus",
                "type": "INTEGER"
            },
            {
                "name": "bpmId",
                "source": "bpmId",
                "type": "TEXT"
            },
            {
                "name": "canApprove",
                "source": "canApprove",
                "type": "INTEGER"
            },
            {
                "name": "canDelete",
                "source": "canDelete",
                "type": "INTEGER"
            },
            {
                "name": "canEdit",
                "source": "canEdit",
                "type": "INTEGER"
            },
            {
                "name": "canRecall",
                "source": "canRecall",
                "type": "INTEGER"
            },
            {
                "name": "constrSchemeDateTime",
                "source": "constrSchemeDateTime",
                "type": "TEXT"
            },
            {
                "name": "constrSchemeFileId",
                "source": "constrSchemeFileId",
                "type": "TEXT"
            },
            {
                "name": "constrSchemeFileName",
                "source": "constrSchemeFileName",
                "type": "TEXT"
            },
            {
                "name": "constrSchemeId",
                "source": "constrSchemeId",
                "type": "TEXT"
            },
            {
                "name": "extra",
                "source": "extra",
                "type": "TEXT"
            },
            {
                "name": "fileName",
                "source": "fileName",
                "type": "TEXT"
            },
            {
                "name": "flowRole",
                "source": "flowRole",
                "type": "INTEGER"
            },
            {
                "name": "id",
                "source": "id",
                "type": "TEXT"
            },
            {
                "name": "instanceId",
                "source": "instanceId",
                "type": "TEXT"
            },
            {
                "name": "prjCode",
                "source": "prjCode",
                "type": "TEXT"
            },
            {
                "name": "prjManageMode",
                "source": "prjManageMode",
                "type": "INTEGER"
            },
            {
                "name": "sigPrjCode",
                "source": "sigPrjCode",
                "type": "TEXT"
            },
            {
                "name": "signaturesStatus",
                "source": "signaturesStatus",
                "type": "INTEGER"
            },
            {
                "name": "traceId",
                "source": "traceId",
                "type": "TEXT"
            }
        ],
        "dataset_key": "dataset_98117e03",
        "key_candidates": [
            "id",
            "prjCode"
        ],
        "page_name": "项目管理实施规划",
        "parent_record_path": null,
        "partition_field": "prjCode",
        "partition_key": "prjCode",
        "plugin_id": "dcp-dataset-98117e03",
        "record_path": "raw_event",
        "record_type": "construction_outline:raw_event",
        "table": "canonical_p061_page_98117e03__construction_outline__raw_event"
    },
    {
        "api_name": "construction_outline",
        "api_path": "/apit/ebuild2-domain-project-stage/v1/implementPlanning/queryImplementPlanningPage",
        "columns": [
            {
                "name": "bidSectCode",
                "source": "bidSectCode",
                "type": "TEXT"
            },
            {
                "name": "bidSectCodeList",
                "source": "bidSectCodeList",
                "type": "TEXT"
            },
            {
                "name": "extra",
                "source": "extra",
                "type": "TEXT"
            },
            {
                "name": "prjCode",
                "source": "prjCode",
                "type": "TEXT"
            },
            {
                "name": "relaFlag",
                "source": "relaFlag",
                "type": "TEXT"
            },
            {
                "name": "singleProjectCode",
                "source": "singleProjectCode",
                "type": "TEXT"
            },
            {
                "name": "singleProjectName",
                "source": "singleProjectName",
                "type": "TEXT"
            },
            {
                "name": "singleProjectType",
                "source": "singleProjectType",
                "type": "INTEGER"
            },
            {
                "name": "traceId",
                "source": "traceId",
                "type": "TEXT"
            }
        ],
        "dataset_key": "dataset_98117e03",
        "key_candidates": [
            "prjCode",
            "singleProjectCode",
            "prjCode+singleProjectCode"
        ],
        "page_name": "项目管理实施规划",
        "parent_record_path": "raw_event",
        "partition_field": "prjCode",
        "partition_key": "prjCode",
        "plugin_id": "dcp-dataset-98117e03",
        "record_path": "raw_event.sinPrjList[]",
        "record_type": "construction_outline:raw_event.sinPrjList[]",
        "table": "canonical_p061_page_98117e03__construction_outline__raw_event_sinprjlist_items"
    },
    {
        "api_name": "construction_outline",
        "api_path": "/apit/ebuild2-domain-project-stage/v1/implementPlanning/queryImplementPlanningPage",
        "columns": [
            {
                "name": "biddingSectionCode",
                "source": "biddingSectionCode",
                "type": "TEXT"
            },
            {
                "name": "biddingSectionName",
                "source": "biddingSectionName",
                "type": "TEXT"
            },
            {
                "name": "extra",
                "source": "extra",
                "type": "TEXT"
            },
            {
                "name": "prjDeptId",
                "source": "prjDeptId",
                "type": "TEXT"
            },
            {
                "name": "projectDepartmentName",
                "source": "projectDepartmentName",
                "type": "TEXT"
            },
            {
                "name": "relaFlag",
                "source": "relaFlag",
                "type": "TEXT"
            },
            {
                "name": "traceId",
                "source": "traceId",
                "type": "TEXT"
            }
        ],
        "dataset_key": "dataset_98117e03",
        "key_candidates": [
            "biddingSectionCode"
        ],
        "page_name": "项目管理实施规划",
        "parent_record_path": "raw_event.sinPrjList[]",
        "partition_field": "biddingSectionCode",
        "partition_key": "biddingSectionCode",
        "plugin_id": "dcp-dataset-98117e03",
        "record_path": "raw_event.sinPrjList[].sinBidList[]",
        "record_type": "construction_outline:raw_event.sinPrjList[].sinBidList[]",
        "table": "canonical_p061_page_98117e03__construction_outline__raw_event_sinprjlist_items_sinbidlist_items"
    },
    {
        "api_name": "project_department_key_personnel",
        "api_path": "/apit/ebuild2-domain-plan-statistics/v1/dept/queryKeyPersonnelInfo",
        "columns": [
            {
                "name": "idCard",
                "source": "idCard",
                "type": "TEXT"
            },
            {
                "name": "name",
                "source": "name",
                "type": "TEXT"
            },
            {
                "name": "originalIdCard",
                "source": "originalIdCard",
                "type": "TEXT"
            },
            {
                "name": "positionCode",
                "source": "positionCode",
                "type": "TEXT"
            },
            {
                "name": "positionName",
                "source": "positionName",
                "type": "TEXT"
            },
            {
                "name": "unitName",
                "source": "unitName",
                "type": "TEXT"
            }
        ],
        "dataset_key": "dataset_7563ad12",
        "key_candidates": [
            "source_record_key+record_path"
        ],
        "page_name": "项目部关键人员统计",
        "parent_record_path": null,
        "partition_field": null,
        "partition_key": null,
        "plugin_id": "dcp-dataset-7563ad12",
        "record_path": "raw_event",
        "record_type": "project_department_key_personnel:raw_event",
        "table": "canonical_p062_page_7563ad12__project_department_key_personnel__raw_event"
    },
    {
        "api_name": "project_department_key_personnel",
        "api_path": "/apit/ebuild2-domain-plan-statistics/v1/dept/queryKeyPersonnelInfo",
        "columns": [
            {
                "name": "personnelCertificates",
                "source": "personnelCertificates",
                "type": "TEXT"
            },
            {
                "name": "personnelCertificatesText",
                "source": "personnelCertificatesText",
                "type": "TEXT"
            }
        ],
        "dataset_key": "dataset_7563ad12",
        "key_candidates": [
            "source_record_key+record_path"
        ],
        "page_name": "项目部关键人员统计",
        "parent_record_path": "raw_event",
        "partition_field": null,
        "partition_key": null,
        "plugin_id": "dcp-dataset-7563ad12",
        "record_path": "raw_event.personnelCertificates[]",
        "record_type": "project_department_key_personnel:raw_event.personnelCertificates[]",
        "table": "canonical_p062_page_7563ad12__project_department_key_personnel__raw_event_personnelcertificates_items"
    },
    {
        "api_name": "project_department_establishment",
        "api_path": "/apit/ebuild2-domain-plan-statistics/v1/dept/queryProjectDeptDetail",
        "columns": [
            {
                "name": "appointUnitName",
                "source": "appointUnitName",
                "type": "TEXT"
            },
            {
                "name": "departmentTypeName",
                "source": "departmentTypeName",
                "type": "TEXT"
            },
            {
                "name": "deptHeadName",
                "source": "deptHeadName",
                "type": "TEXT"
            },
            {
                "name": "projectDepartmentName",
                "source": "projectDepartmentName",
                "type": "TEXT"
            },
            {
                "name": "projectDeptNo",
                "source": "projectDeptNo",
                "type": "TEXT"
            },
            {
                "name": "unitTypeName",
                "source": "unitTypeName",
                "type": "TEXT"
            }
        ],
        "dataset_key": "dataset_93667e3b",
        "key_candidates": [
            "source_record_key+record_path"
        ],
        "page_name": "项目部组建情况统计",
        "parent_record_path": null,
        "partition_field": null,
        "partition_key": null,
        "plugin_id": "dcp-dataset-93667e3b",
        "record_path": "raw_event",
        "record_type": "project_department_establishment:raw_event",
        "table": "canonical_p063_page_93667e3b__project_department_establishment__raw_event"
    },
    {
        "api_name": "project_evaluation",
        "api_path": "/apit/ebuild2-domain-project-stage/v1/summaryEvaluate/queryDeptSummaryList",
        "columns": [
            {
                "name": "actualCommencementDate",
                "source": "actualCommencementDate",
                "type": "TEXT"
            },
            {
                "name": "actualCommissioningDate",
                "source": "actualCommissioningDate",
                "type": "TEXT"
            },
            {
                "name": "extra",
                "source": "extra",
                "type": "TEXT"
            },
            {
                "name": "plannedCommencementDate",
                "source": "plannedCommencementDate",
                "type": "TEXT"
            },
            {
                "name": "plannedCommissioningDate",
                "source": "plannedCommissioningDate",
                "type": "TEXT"
            },
            {
                "name": "singleProjectCode",
                "source": "singleProjectCode",
                "type": "TEXT"
            },
            {
                "name": "singleProjectName",
                "source": "singleProjectName",
                "type": "TEXT"
            },
            {
                "name": "traceId",
                "source": "traceId",
                "type": "TEXT"
            }
        ],
        "dataset_key": "dataset_ecce9198",
        "key_candidates": [
            "singleProjectCode"
        ],
        "page_name": "项目部评价汇总",
        "parent_record_path": null,
        "partition_field": "singleProjectCode",
        "partition_key": "singleProjectCode",
        "plugin_id": "dcp-dataset-ecce9198",
        "record_path": "raw_event",
        "record_type": "project_evaluation:raw_event",
        "table": "canonical_p064_page_ecce9198__project_evaluation__raw_event"
    },
    {
        "api_name": "project_evaluation",
        "api_path": "/apit/ebuild2-domain-project-stage/v1/summaryEvaluate/queryDeptSummaryList",
        "columns": [
            {
                "name": "departmentType",
                "source": "departmentType",
                "type": "INTEGER"
            },
            {
                "name": "deptId",
                "source": "deptId",
                "type": "TEXT"
            },
            {
                "name": "establishmentDate",
                "source": "establishmentDate",
                "type": "TEXT"
            },
            {
                "name": "evaluateDate",
                "source": "evaluateDate",
                "type": "TEXT"
            },
            {
                "name": "extra",
                "source": "extra",
                "type": "TEXT"
            },
            {
                "name": "personnelId",
                "source": "personnelId",
                "type": "TEXT"
            },
            {
                "name": "personnelName",
                "source": "personnelName",
                "type": "TEXT"
            },
            {
                "name": "positionCode",
                "source": "positionCode",
                "type": "TEXT"
            },
            {
                "name": "positionName",
                "source": "positionName",
                "type": "TEXT"
            },
            {
                "name": "projectDepartmentName",
                "source": "projectDepartmentName",
                "type": "TEXT"
            },
            {
                "name": "projectDeptNo",
                "source": "projectDeptNo",
                "type": "TEXT"
            },
            {
                "name": "sunType",
                "source": "sunType",
                "type": "INTEGER"
            },
            {
                "name": "totalPoints",
                "source": "totalPoints",
                "type": "REAL"
            },
            {
                "name": "traceId",
                "source": "traceId",
                "type": "TEXT"
            }
        ],
        "dataset_key": "dataset_ecce9198",
        "key_candidates": [
            "source_record_key+record_path"
        ],
        "page_name": "项目部评价汇总",
        "parent_record_path": "raw_event",
        "partition_field": null,
        "partition_key": null,
        "plugin_id": "dcp-dataset-ecce9198",
        "record_path": "raw_event.summaryEvaluateDeptDTOList[]",
        "record_type": "project_evaluation:raw_event.summaryEvaluateDeptDTOList[]",
        "table": "canonical_p064_page_ecce9198__project_evaluation__raw_event_summaryevaluatedeptdtolist_items"
    },
    {
        "api_name": "risk_ledger_list",
        "api_path": "/apit/ebuild2-domain-security-risk/v1/projectRiskLedger/queryPage",
        "columns": [
            {
                "name": "assessmentRiskLevel",
                "source": "assessmentRiskLevel",
                "type": "INTEGER"
            },
            {
                "name": "assessmentRiskLevelText",
                "source": "assessmentRiskLevelText",
                "type": "TEXT"
            },
            {
                "name": "biddingSectionCode",
                "source": "biddingSectionCode",
                "type": "TEXT"
            },
            {
                "name": "biddingSectionName",
                "source": "biddingSectionName",
                "type": "TEXT"
            },
            {
                "name": "buildUnitCode",
                "source": "buildUnitCode",
                "type": "TEXT"
            },
            {
                "name": "consequenceDueToRisk",
                "source": "consequenceDueToRisk",
                "type": "TEXT"
            },
            {
                "name": "deleteFlag",
                "source": "deleteFlag",
                "type": "INTEGER"
            },
            {
                "name": "endTime",
                "source": "endTime",
                "type": "TEXT"
            },
            {
                "name": "executeTime",
                "source": "executeTime",
                "type": "TEXT"
            },
            {
                "name": "extra",
                "source": "extra",
                "type": "TEXT"
            },
            {
                "name": "huvFlag",
                "source": "huvFlag",
                "type": "INTEGER"
            },
            {
                "name": "id",
                "source": "id",
                "type": "TEXT"
            },
            {
                "name": "machs",
                "source": "machs",
                "type": "TEXT"
            },
            {
                "name": "merge",
                "source": "merge",
                "type": "TEXT"
            },
            {
                "name": "meths",
                "source": "meths",
                "type": "TEXT"
            },
            {
                "name": "minConstrHeadcount",
                "source": "minConstrHeadcount",
                "type": "TEXT"
            },
            {
                "name": "partSubentry",
                "source": "partSubentry",
                "type": "TEXT"
            },
            {
                "name": "plannedStartDate",
                "source": "plannedStartDate",
                "type": "TEXT"
            },
            {
                "name": "preventCtrlMeasure",
                "source": "preventCtrlMeasure",
                "type": "TEXT"
            },
            {
                "name": "preventCtrlMeasureEnvironment",
                "source": "preventCtrlMeasureEnvironment",
                "type": "TEXT"
            },
            {
                "name": "preventWeeklyCtrlMeasure",
                "source": "preventWeeklyCtrlMeasure",
                "type": "TEXT"
            },
            {
                "name": "prjCode",
                "source": "prjCode",
                "type": "TEXT"
            },
            {
                "name": "prjName",
                "source": "prjName",
                "type": "TEXT"
            },
            {
                "name": "professional",
                "source": "professional",
                "type": "TEXT"
            },
            {
                "name": "publishState",
                "source": "publishState",
                "type": "TEXT"
            },
            {
                "name": "publishStateText",
                "source": "publishStateText",
                "type": "TEXT"
            },
            {
                "name": "reAssessmentRiskLevel",
                "source": "reAssessmentRiskLevel",
                "type": "INTEGER"
            },
            {
                "name": "reAssessmentRiskLevelText",
                "source": "reAssessmentRiskLevelText",
                "type": "TEXT"
            },
            {
                "name": "remark",
                "source": "remark",
                "type": "TEXT"
            },
            {
                "name": "riskAssessmentValue",
                "source": "riskAssessmentValue",
                "type": "TEXT"
            },
            {
                "name": "riskControlKeyFactor",
                "source": "riskControlKeyFactor",
                "type": "TEXT"
            },
            {
                "name": "riskNo",
                "source": "riskNo",
                "type": "TEXT"
            },
            {
                "name": "riskStatus",
                "source": "riskStatus",
                "type": "TEXT"
            },
            {
                "name": "riskStatusText",
                "source": "riskStatusText",
                "type": "TEXT"
            },
            {
                "name": "singleProjectCode",
                "source": "singleProjectCode",
                "type": "TEXT"
            },
            {
                "name": "singleProjectName",
                "source": "singleProjectName",
                "type": "TEXT"
            },
            {
                "name": "sourceRiskPrecautionId",
                "source": "sourceRiskPrecautionId",
                "type": "TEXT"
            },
            {
                "name": "ticketId",
                "source": "ticketId",
                "type": "TEXT"
            },
            {
                "name": "ticketNo",
                "source": "ticketNo",
                "type": "TEXT"
            },
            {
                "name": "towerIds",
                "source": "towerIds",
                "type": "TEXT"
            },
            {
                "name": "traceId",
                "source": "traceId",
                "type": "TEXT"
            },
            {
                "name": "updateTime",
                "source": "updateTime",
                "type": "TEXT"
            },
            {
                "name": "updater",
                "source": "updater",
                "type": "TEXT"
            },
            {
                "name": "updaterId",
                "source": "updaterId",
                "type": "TEXT"
            },
            {
                "name": "voltageDrpFlag",
                "source": "voltageDrpFlag",
                "type": "INTEGER"
            },
            {
                "name": "workContent",
                "source": "workContent",
                "type": "TEXT"
            },
            {
                "name": "workProcedure",
                "source": "workProcedure",
                "type": "TEXT"
            },
            {
                "name": "workSite",
                "source": "workSite",
                "type": "TEXT"
            },
            {
                "name": "workSiteId",
                "source": "workSiteId",
                "type": "TEXT"
            },
            {
                "name": "workSiteName",
                "source": "workSiteName",
                "type": "TEXT"
            },
            {
                "name": "workSiteType",
                "source": "workSiteType",
                "type": "INTEGER"
            },
            {
                "name": "workType",
                "source": "workType",
                "type": "TEXT"
            },
            {
                "name": "workingCondition",
                "source": "workingCondition",
                "type": "TEXT"
            },
            {
                "name": "workingConditionFlag",
                "source": "workingConditionFlag",
                "type": "INTEGER"
            },
            {
                "name": "workingConditionText",
                "source": "workingConditionText",
                "type": "TEXT"
            }
        ],
        "dataset_key": "dataset_0a75165a",
        "key_candidates": [
            "id",
            "prjCode",
            "singleProjectCode",
            "biddingSectionCode",
            "ticketId",
            "prjCode+singleProjectCode+biddingSectionCode"
        ],
        "page_name": "风险底数一本账",
        "parent_record_path": null,
        "partition_field": "prjCode",
        "partition_key": "prjCode",
        "plugin_id": "dcp-dataset-0a75165a",
        "record_path": "raw_event",
        "record_type": "risk_ledger_list:raw_event",
        "table": "canonical_p065_page_0a75165a__risk_ledger_list__raw_event"
    },
    {
        "api_name": "risk_ledger_list",
        "api_path": "/apit/ebuild2-domain-security-risk/v1/projectRiskLedger/queryPage",
        "columns": [
            {
                "name": "extra",
                "source": "extra",
                "type": "TEXT"
            },
            {
                "name": "machId",
                "source": "machId",
                "type": "TEXT"
            },
            {
                "name": "machName",
                "source": "machName",
                "type": "TEXT"
            },
            {
                "name": "traceId",
                "source": "traceId",
                "type": "TEXT"
            }
        ],
        "dataset_key": "dataset_0a75165a",
        "key_candidates": [
            "source_record_key+record_path"
        ],
        "page_name": "风险底数一本账",
        "parent_record_path": "raw_event",
        "partition_field": null,
        "partition_key": null,
        "plugin_id": "dcp-dataset-0a75165a",
        "record_path": "raw_event.machs[]",
        "record_type": "risk_ledger_list:raw_event.machs[]",
        "table": "canonical_p065_page_0a75165a__risk_ledger_list__raw_event_machs_items"
    },
    {
        "api_name": "page",
        "api_path": "/apit/ebuild2-domain-quality-accept/v1/divide/page",
        "columns": [
            {
                "name": "bidSectCode",
                "source": "bidSectCode",
                "type": "TEXT"
            },
            {
                "name": "bidSectName",
                "source": "bidSectName",
                "type": "TEXT"
            },
            {
                "name": "bpmId",
                "source": "bpmId",
                "type": "TEXT"
            },
            {
                "name": "bpmType",
                "source": "bpmType",
                "type": "INTEGER"
            },
            {
                "name": "compileDate",
                "source": "compileDate",
                "type": "TEXT"
            },
            {
                "name": "createProcessStatus",
                "source": "createProcessStatus",
                "type": "TEXT"
            },
            {
                "name": "divideName",
                "source": "divideName",
                "type": "TEXT"
            },
            {
                "name": "extra",
                "source": "extra",
                "type": "TEXT"
            },
            {
                "name": "fileId",
                "source": "fileId",
                "type": "TEXT"
            },
            {
                "name": "id",
                "source": "id",
                "type": "TEXT"
            },
            {
                "name": "instanceId",
                "source": "instanceId",
                "type": "TEXT"
            },
            {
                "name": "prjCode",
                "source": "prjCode",
                "type": "TEXT"
            },
            {
                "name": "prjName",
                "source": "prjName",
                "type": "TEXT"
            },
            {
                "name": "prjType",
                "source": "prjType",
                "type": "INTEGER"
            },
            {
                "name": "processStatus",
                "source": "processStatus",
                "type": "INTEGER"
            },
            {
                "name": "provinceCode",
                "source": "provinceCode",
                "type": "TEXT"
            },
            {
                "name": "resetFlag",
                "source": "resetFlag",
                "type": "INTEGER"
            },
            {
                "name": "sinPrjCode",
                "source": "sinPrjCode",
                "type": "TEXT"
            },
            {
                "name": "sinPrjName",
                "source": "sinPrjName",
                "type": "TEXT"
            },
            {
                "name": "templateName",
                "source": "templateName",
                "type": "TEXT"
            },
            {
                "name": "traceId",
                "source": "traceId",
                "type": "TEXT"
            },
            {
                "name": "uhvFlag",
                "source": "uhvFlag",
                "type": "TEXT"
            },
            {
                "name": "userId",
                "source": "userId",
                "type": "TEXT"
            },
            {
                "name": "userNode",
                "source": "userNode",
                "type": "TEXT"
            },
            {
                "name": "voltageLevel",
                "source": "voltageLevel",
                "type": "TEXT"
            },
            {
                "name": "wordTemplateId",
                "source": "wordTemplateId",
                "type": "TEXT"
            }
        ],
        "dataset_key": "dataset_74015418",
        "key_candidates": [
            "id",
            "prjCode"
        ],
        "page_name": "验收范围划分",
        "parent_record_path": null,
        "partition_field": "prjCode",
        "partition_key": "prjCode",
        "plugin_id": "dcp-dataset-74015418",
        "record_path": "raw_event",
        "record_type": "page:raw_event",
        "table": "canonical_p066_page_74015418__page__raw_event"
    },
    {
        "api_name": "queryToolBoxTalkListPagePc",
        "api_path": "/apit/ebuild2-domain-security-work/v1/toolBoxTalk/queryToolBoxTalkListPagePc",
        "columns": [
            {
                "name": "id",
                "source": "id",
                "type": "TEXT"
            },
            {
                "name": "workDate",
                "source": "workDate",
                "type": "TEXT"
            },
            {
                "name": "toolBoxTalkLongitude",
                "source": "toolBoxTalkLongitude",
                "type": "TEXT"
            },
            {
                "name": "toolBoxTalkLatitude",
                "source": "toolBoxTalkLatitude",
                "type": "TEXT"
            },
            {
                "name": "currentConstrHeadcount",
                "source": "currentConstrHeadcount",
                "type": "INTEGER"
            },
            {
                "name": "reAssessmentRiskLevel",
                "source": "reAssessmentRiskLevel",
                "type": "TEXT"
            },
            {
                "name": "currentConstructionStatus",
                "source": "currentConstructionStatus",
                "type": "TEXT"
            },
            {
                "name": "prjCode",
                "source": "prjCode",
                "type": "TEXT"
            },
            {
                "name": "prjName",
                "source": "prjName",
                "type": "TEXT"
            },
            {
                "name": "singleProjectCode",
                "source": "singleProjectCode",
                "type": "TEXT"
            },
            {
                "name": "singleProjectName",
                "source": "singleProjectName",
                "type": "TEXT"
            },
            {
                "name": "biddingSectionCode",
                "source": "biddingSectionCode",
                "type": "TEXT"
            },
            {
                "name": "biddingSectionName",
                "source": "biddingSectionName",
                "type": "TEXT"
            },
            {
                "name": "voltageLevel",
                "source": "voltageLevel",
                "type": "TEXT"
            },
            {
                "name": "city",
                "source": "city",
                "type": "TEXT"
            },
            {
                "name": "currentConstrDate",
                "source": "currentConstrDate",
                "type": "TEXT"
            },
            {
                "name": "workStartTime",
                "source": "workStartTime",
                "type": "TEXT"
            }
        ],
        "dataset_key": "daily_meeting",
        "key_candidates": [
            "id",
            "prjCode",
            "singleProjectCode",
            "biddingSectionCode",
            "prjCode+singleProjectCode+biddingSectionCode"
        ],
        "page_name": "?????",
        "parent_record_path": null,
        "partition_field": "currentConstrDate",
        "partition_key": "currentConstrDate",
        "plugin_id": "dcp-daily-meeting",
        "record_path": "raw_event",
        "record_type": "queryToolBoxTalkListPagePc:raw_event",
        "sample_override": "sample list is empty; fields come from MVP live daily meeting contract",
        "table": "canonical_p_daily_meeting__queryToolBoxTalkListPagePc__raw_event"
    },
    {
        "api_name": "substation_coordinates",
        "api_path": "/apit/ebuild2-domain-project-stage/v1/substationCoordinates/querySubstationCoordinates",
        "columns": [
            {
                "name": "id",
                "source": "id",
                "type": "TEXT"
            },
            {
                "name": "prjCode",
                "source": "prjCode",
                "type": "TEXT"
            },
            {
                "name": "singleProjectCode",
                "source": "singleProjectCode",
                "type": "TEXT"
            },
            {
                "name": "singleProjectName",
                "source": "singleProjectName",
                "type": "TEXT"
            },
            {
                "name": "biddingSectionCode",
                "source": "biddingSectionCode",
                "type": "TEXT"
            },
            {
                "name": "longitude",
                "source": "longitude",
                "type": "TEXT"
            },
            {
                "name": "latitude",
                "source": "latitude",
                "type": "TEXT"
            }
        ],
        "dataset_key": "station",
        "key_candidates": [
            "id",
            "prjCode",
            "singleProjectCode",
            "biddingSectionCode",
            "prjCode+singleProjectCode+biddingSectionCode"
        ],
        "page_name": "?????",
        "parent_record_path": null,
        "partition_field": "prjCode",
        "partition_key": "prjCode",
        "plugin_id": "dcp-station",
        "record_path": "raw_event",
        "record_type": "substation_coordinates:raw_event",
        "sample_override": "sample data is null; fields come from live MVP station contract",
        "table": "canonical_p_station__substation_coordinates__raw_event"
    },
    {
        "api_name": "section_details",
        "api_path": "/apit/ebuild2-common-project-digitization/section/getSectionInfo",
        "columns": [
            {
                "name": "id",
                "source": "id",
                "type": "TEXT"
            },
            {
                "name": "prjCode",
                "source": "prjCode",
                "type": "TEXT"
            },
            {
                "name": "prjName",
                "source": "prjName",
                "type": "TEXT"
            },
            {
                "name": "singleProjectCode",
                "source": "singleProjectCode",
                "type": "TEXT"
            },
            {
                "name": "singleProjectName",
                "source": "singleProjectName",
                "type": "TEXT"
            },
            {
                "name": "biddingSectionCode",
                "source": "biddingSectionCode",
                "type": "TEXT"
            },
            {
                "name": "biddingSectionName",
                "source": "biddingSectionName",
                "type": "TEXT"
            },
            {
                "name": "sectionName",
                "source": "sectionName",
                "type": "TEXT"
            },
            {
                "name": "startTowerNo",
                "source": "startTowerNo",
                "type": "TEXT"
            },
            {
                "name": "endTowerNo",
                "source": "endTowerNo",
                "type": "TEXT"
            }
        ],
        "dataset_key": "line_section",
        "key_candidates": [
            "id",
            "prjCode",
            "singleProjectCode",
            "biddingSectionCode",
            "prjCode+singleProjectCode+biddingSectionCode"
        ],
        "page_name": "????",
        "parent_record_path": null,
        "partition_field": "prjCode",
        "partition_key": "prjCode",
        "plugin_id": "dcp-line-section",
        "record_path": "raw_event",
        "record_type": "section_details:raw_event",
        "sample_override": "sample is an error response; fields come from MVP live line section contract",
        "table": "canonical_p_line_section__section_details__raw_event"
    }
]


def tables_for_api(api_name: str, dataset_key: str | None = None) -> list[dict]:
    return [entry for entry in DCP_RESPONSE_TABLES if entry["api_name"] == api_name and (dataset_key is None or entry["dataset_key"] == dataset_key)]

def table_for_record(api_name: str, record_path: str, dataset_key: str | None = None) -> dict | None:
    for entry in tables_for_api(api_name, dataset_key=dataset_key):
        if entry["record_path"] == record_path:
            return entry
    return None

def dataset_plugins() -> dict[str, dict]:
    plugins: dict[str, dict] = {}
    for entry in DCP_RESPONSE_TABLES:
        plugin_id = entry["plugin_id"]
        plugin = plugins.setdefault(plugin_id, {"plugin_id": plugin_id, "downloader_name": "vibe-downloader-dcp", "source_system": "dcp", "dataset_keys": [], "canonical_tables": []})
        if entry["dataset_key"] not in plugin["dataset_keys"]:
            plugin["dataset_keys"].append(entry["dataset_key"])
        plugin["canonical_tables"].append(entry["table"])
    return plugins
