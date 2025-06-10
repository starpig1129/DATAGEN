from core.state import State
from typing import Literal, Union, Dict, List, Optional
from langchain_core.messages import AIMessage
import logging
import json
import ast
import re

# Set up logger
logger = logging.getLogger(__name__)

# Define types for node routing
NodeType = Literal['Visualization', 'Search', 'Coder', 'Report', 'Process', 'NoteTaker', 'Hypothesis', 'QualityReview']
ProcessNodeType = Literal['Coder', 'Search', 'Visualization', 'Report', 'Process', 'Refiner']

def hypothesis_router(state: State) -> NodeType:
    """
    Route based on the presence of a hypothesis and user decisions in the state.

    Args:
        state (State): The current state of the system.

    Returns:
        NodeType: 'Hypothesis' if no hypothesis exists or user chose to regenerate,
                 otherwise 'Process'.
    """
    logger.info("Entering hypothesis_router")
    hypothesis: Union[AIMessage, str, None] = state.get("hypothesis")
    
    # 檢查用戶是否明確選擇繼續研究
    force_process = state.get("force_process", False)
    user_choice_continue = state.get("user_choice_continue", False)
    process_decision = state.get("process_decision", "")
    
    # 添加詳細的調試信息
    print(f"=== hypothesis_router 調試 ===")
    print(f"原始hypothesis值: {repr(hypothesis)}")
    print(f"hypothesis類型: {type(hypothesis)}")
    print(f"state中的process: {state.get('process', 'None')}")
    print(f"state中的sender: {state.get('sender', 'None')}")
    print(f"force_process: {force_process}")
    print(f"user_choice_continue: {user_choice_continue}")
    print(f"process_decision: '{process_decision}'")
    
    # 如果用戶明確選擇繼續研究，直接路由到Process
    # 關鍵修復：同時檢查 process_decision 為 "2"（繼續研究）
    user_chose_continue = (
        force_process or
        user_choice_continue or
        process_decision.strip() == "2"
    )
    
    if user_chose_continue:
        logger.info("User explicitly chose to continue research, routing to Process")
        print("=== 用戶明確選擇繼續研究，路由到Process ===")
        # 清除所有決策標誌，確保狀態一致性
        state["force_process"] = False
        state["user_choice_continue"] = False
        state["process_decision"] = ""  # 現在才安全清除 process_decision
        # 關鍵修復：清除 needs_decision 狀態，確保決策處理完成
        state["needs_decision"] = False
        print("已清除所有決策標誌，包括 needs_decision")
        return "Process"
    
    try:
        if isinstance(hypothesis, AIMessage):
            hypothesis_content = hypothesis.content
            logger.debug("Hypothesis is an AIMessage")
        elif isinstance(hypothesis, str):
            hypothesis_content = hypothesis
            logger.debug("Hypothesis is a string")
        else:
            hypothesis_content = ""
            logger.warning(f"Unexpected hypothesis type: {type(hypothesis)}")
            
        if not isinstance(hypothesis_content, str):
            hypothesis_content = str(hypothesis_content)
            logger.warning("Converting hypothesis content to string")
    except Exception as e:
        logger.error(f"Error processing hypothesis: {e}")
        hypothesis_content = ""
    
    print(f"處理後的hypothesis_content: '{hypothesis_content}'")
    print(f"hypothesis_content.strip(): '{hypothesis_content.strip()}'")
    print(f"not hypothesis_content.strip(): {not hypothesis_content.strip()}")
    
    result = "Hypothesis" if not hypothesis_content.strip() else "Process"
    logger.info(f"hypothesis_router decision: {result}")
    print(f"=== hypothesis_router 決策: {result} ===")
    return result

def QualityReview_router(state: State) -> NodeType:
    """
    Route based on the quality review outcome and process decision.

    Args:
    state (State): The current state of the system.

    Returns:
    NodeType: The next node to route to based on the quality review and process decision.
    """
    logger.info("Entering QualityReview_router")
    messages = state.get("messages", [])
    last_message = messages[-1] if messages else None
    
    # Check if revision is needed
    if (last_message and 'REVISION' in str(last_message.content)) or state.get("needs_revision", False):
        previous_node = state.get("last_sender", "")
        revision_routes = {
            "Visualization": "Visualization",
            "Search": "Search",
            "Coder": "Coder",
            "Report": "Report"
        }
        result = revision_routes.get(previous_node, "NoteTaker")
        logger.info(f"Revision needed. Routing to: {result}")
        return result
    
    else:
        return "NoteTaker"
    

def extract_decision_from_any_format(process_decision: Union[AIMessage, Dict, str, None]) -> str:
    """
    統一的決策提取函數，處理字典、字符串、AIMessage 等格式
    
    Args:
        process_decision: 各種格式的決策數據
        
    Returns:
        str: 提取出的決策字符串
    """
    if isinstance(process_decision, dict):
        # 直接從字典獲取 'next' 值（核心修復）
        decision = process_decision.get('next', '')
        if isinstance(decision, str):
            return decision.strip()
        return str(decision).strip()
    
    elif isinstance(process_decision, AIMessage):
        content = process_decision.content.strip()
        
        # 嘗試解析 Python 字典格式的字串
        try:
            # 首先嘗試使用 ast.literal_eval 安全解析 Python 字典
            decision_dict = ast.literal_eval(content)
            if isinstance(decision_dict, dict):
                decision = decision_dict.get('next', '')
                return str(decision).strip() if decision else ''
        except (ValueError, SyntaxError):
            pass
        
        # 嘗試使用正則表達式提取 'next' 值
        try:
            # 匹配 'next': 'value' 或 "next": "value" 格式
            next_match = re.search(r"['\"]next['\"]:\s*['\"]([^'\"]+)['\"]", content)
            if next_match:
                return next_match.group(1).strip()
        except Exception:
            pass
        
        # 如果正則表達式也失敗，嘗試簡單的字串替換
        if "'" in content and '"' not in content:
            try:
                # 只有在內容不包含撇號時才進行替換
                if content.count("'") == content.count("'"):  # 檢查撇號配對
                    decision_dict = json.loads(content.replace("'", '"'))
                    decision = decision_dict.get('next', '')
                    return str(decision).strip() if decision else ''
            except json.JSONDecodeError:
                pass
        
        # 如果所有解析都失敗，返回原始內容
        return content
    
    elif isinstance(process_decision, str):
        content = process_decision.strip()
        
        # 嘗試解析字符串化的字典格式
        if content.startswith('{') and content.endswith('}'):
            try:
                # 首先嘗試使用 ast.literal_eval 安全解析 Python 字典
                decision_dict = ast.literal_eval(content)
                if isinstance(decision_dict, dict):
                    decision = decision_dict.get('next', '')
                    return str(decision).strip() if decision else ''
            except (ValueError, SyntaxError):
                pass
            
            # 嘗試使用正則表達式提取 'next' 值
            try:
                # 匹配 'next': 'value' 或 "next": "value" 格式
                next_match = re.search(r"['\"]next['\"]:\s*['\"]([^'\"]+)['\"]", content)
                if next_match:
                    return next_match.group(1).strip()
            except Exception:
                pass
            
            # 嘗試簡單的字串替換（僅當安全時）
            if "'" in content and '"' not in content:
                try:
                    # 檢查撇號配對，確保安全替換
                    if content.count("'") % 2 == 0:  # 撇號必須成對出現
                        decision_dict = json.loads(content.replace("'", '"'))
                        if isinstance(decision_dict, dict):
                            decision = decision_dict.get('next', '')
                            return str(decision).strip() if decision else ''
                except json.JSONDecodeError:
                    pass
        
        # 如果不是字典格式或解析失敗，返回原始字符串
        return content
    
    else:
        return str(process_decision).strip() if process_decision else ''


def process_router(state: State) -> ProcessNodeType:
    """
    Route based on the process decision in the state.
    
    修復重點：
    1. 正確處理 process_agent 輸出的字典格式
    2. 統一數據格式處理
    3. 添加防循環機制
    4. 增強診斷日誌

    Args:
        state (State): The current state of the system.

    Returns:
        ProcessNodeType: The next process node to route to based on the process decision.
    """
    logger.info("Entering process_router")
    process_decision: Union[AIMessage, Dict, str, None] = state.get("process_decision", "")
    
    # 防循環機制：檢查連續失敗次數
    consecutive_failures = state.get("process_router_failures", 0)
    MAX_FAILURES = 3
    
    # 添加詳細的調試信息
    print(f"=== process_router 調試 ===")
    print(f"原始process_decision值: {repr(process_decision)}")
    print(f"process_decision類型: {type(process_decision)}")
    print(f"state中的sender: {state.get('sender', 'None')}")
    print(f"連續失敗次數: {consecutive_failures}")
    
    # 防循環機制：如果連續失敗太多次，使用緊急處理
    if consecutive_failures >= MAX_FAILURES:
        logger.error(f"檢測到連續 {consecutive_failures} 次路由失敗，啟動緊急處理")
        print(f"=== 緊急處理：連續失敗 {consecutive_failures} 次，強制路由到 Coder ===")
        
        # 重置失敗計數器並強制路由到 Coder
        state["process_router_failures"] = 0
        state["emergency_routing"] = True
        return "Coder"
    
    decision_str: str = ""
    
    try:
        # 使用統一的決策提取函數
        decision_str = extract_decision_from_any_format(process_decision)
        
        print(f"統一提取後的 decision_str: {repr(decision_str)}")
        
        # 特別處理字典格式的詳細日誌
        if isinstance(process_decision, dict):
            logger.info(f"檢測到字典格式決策: {process_decision}")
            print(f"字典內容: {process_decision}")
            print(f"提取的next值: {repr(decision_str)}")
        
    except Exception as e:
        logger.error(f"決策提取過程發生錯誤: {e}")
        decision_str = ""
    
    # Define valid decisions
    valid_decisions = {"Coder", "Search", "Visualization", "Report"}
    
    print(f"最終解析出的 decision_str: {repr(decision_str)}")
    print(f"有效決策列表: {valid_decisions}")
    print(f"決策是否有效: {decision_str in valid_decisions}")
    
    # 檢查是否是有效決策
    if decision_str and decision_str in valid_decisions:
        logger.info(f"✅ 有效的process決策: {decision_str}")
        print(f"=== process_router 決策: {decision_str} (有效) ===")
        
        # 重置失敗計數器
        state["process_router_failures"] = 0
        return decision_str
    
    # 檢查是否是結束指令
    if decision_str == "FINISH":
        logger.info("Process決策是FINISH，結束流程")
        print(f"=== process_router 決策: Refiner (FINISH) ===")
        
        # 重置失敗計數器
        state["process_router_failures"] = 0
        return "Refiner"
    
    # 決策無效或為空的處理
    logger.warning(f"❌ 無效或空的process決策: '{decision_str}'")
    print(f"決策內容: '{decision_str}'")
    print(f"是否為空: {not decision_str}")
    print(f"是否在有效列表中: {decision_str in valid_decisions}")
    
    # 增加失敗計數器
    state["process_router_failures"] = consecutive_failures + 1
    
    # 如果是首次失敗，提供更詳細的診斷信息
    if consecutive_failures == 0:
        logger.warning("首次路由失敗，嘗試診斷問題...")
        print(f"=== 首次路由失敗診斷 ===")
        print(f"原始決策類型: {type(process_decision)}")
        print(f"原始決策內容: {repr(process_decision)}")
        
        if isinstance(process_decision, dict):
            print(f"字典鍵: {list(process_decision.keys())}")
            print(f"next值存在: {'next' in process_decision}")
            print(f"next值內容: {repr(process_decision.get('next'))}")
    
    logger.warning(f"默認回到 'Process'，失敗計數: {consecutive_failures + 1}")
    print(f"=== process_router 決策: Process (invalid/empty，失敗 #{consecutive_failures + 1}) ===")
    return "Process"

logger.info("Router module initialized")
