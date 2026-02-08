import asyncio
import logging
from typing import Dict, Optional
import importlib.util

# 设置日志
import os
log_dir = os.path.join(os.path.dirname(__file__), "../logs")
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, "translator.log")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class Translator:
    def __init__(self):
        self.llm_instance = None
        self.inference_mode = "cpu"  # 默认CPU模式
        self._need_recreate = False  # 标记是否需要重新创建实例
    
    async def init(self):
        """初始化翻译器"""
        logger.info("翻译器初始化完成")
    
    async def cleanup(self):
        """清理翻译器资源"""
        if self.llm_instance:
            try:
                del self.llm_instance
            except:
                pass
            self.llm_instance = None
        logger.info("翻译器资源清理完成")
    
    async def translate(self, text: str, source_lang: str = "auto", target_lang: str = "zh", provider: str = "llama-cpp") -> Dict[str, str]:
        """
        统一的翻译接口
        """
        if provider == "llama-cpp":
            return await self.translate_with_llama_cpp(text, source_lang, target_lang)
        elif provider == "baidu":
            return await self.translate_with_baidu(text, source_lang, target_lang)
        else:
            return {
                "success": False,
                "error": f"不支持的翻译提供商: {provider}"
            }
    
    async def translate_with_llama_cpp(self, text: str, source_lang: str = "auto", target_lang: str = "zh") -> Dict[str, str]:
        """
        使用llama-cpp-python加载GGUF模型进行翻译 (仅CPU模式)
        """
        try:
            # 动态导入，避免在没有安装时出错
            from llama_cpp import Llama
            import json
            import os
            
            # 从配置文件加载参数
            config_path = "../config.json"
            config_file_path = os.path.join(os.path.dirname(__file__), config_path)
            config = {}
            if os.path.exists(config_file_path):
                with open(config_file_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
            
            # 使用配置文件中的参数，如果没有则使用默认值
            model_dir = config.get("model_dir", "./models")
            current_model = config.get("current_model", "")
            context_length = config.get("context_length", 2048)
            threads = config.get("threads", 4)
            max_tokens = config.get("max_tokens", 512)
            temperature = config.get("temperature", 0.1)
            
            # 构建模型路径
            if not os.path.isabs(model_dir):
                base_dir = os.path.dirname(__file__)
                model_dir = os.path.join(base_dir, "..", model_dir)
                model_dir = os.path.normpath(model_dir)
            
            # 如果没有指定当前模型，尝试查找第一个 .gguf 文件
            if not current_model:
                if os.path.exists(model_dir):
                    for file in os.listdir(model_dir):
                        if file.endswith('.gguf'):
                            current_model = file
                            break
            
            if not current_model:
                return {
                    "success": False,
                    "error": f"模型文件夹中没有找到 .gguf 文件: {model_dir}"
                }
            
            model_path = os.path.join(model_dir, current_model)
            
            # 注意：用户需要先下载合适的GGUF翻译模型文件
            # 这里提供一个通用的翻译提示模板
            # 实际使用时需要一个专门的翻译模型，如Qwen、Mistral等微调模型
            
            # 构建翻译提示（使用混元模型的提示词模板）
            # 根据目标语言构建提示词
            target_lang_map = {
                "zh": "中文",
                "en": "English",
                "ja": "日本語",
                "ko": "한국어",
                "fr": "Français",
                "de": "Deutsch",
                "es": "Español",
                "ru": "Русский",
                "ar": "العربية",
                "it": "Italiano",
                "pt": "Português",
                "nl": "Nederlands",
                "pl": "Polski",
                "vi": "Tiếng Việt",
                "th": "ไทย",
                "tr": "Türkçe",
                "he": "עברית",
                "hi": "हिन्दी",
                "cs": "Čeština",
                "uk": "Українська",
                "id": "Bahasa Indonesia",
                "ms": "Bahasa Melayu",
                "tl": "Filipino",
                "bn": "বাংলা",
                "ta": "தமிழ்",
                "te": "తెలుగు",
                "mr": "मराठी",
                "gu": "ગુજરાતી",
                "kn": "ಕನ್ನಡ",
                "ml": "മലയാളം",
                "si": "සිංහල",
                "my": "မြန်မာဘာသာ",
                "km": "ភាសាខ្មែរ",
                "lo": "ລາວ",
                "fa": "فارسی",
                "ur": "اردو",
                "pa": "ਪੰਜਾਬੀ",
                "kk": "Қазақ тілі",
                "uz": "O'zbek tili",
                "mn": "Монгол хэл",
                "bo": "བོད་སྐད།",
                "ug": "ئۇيغۇر تىلى",
                "yue": "粵語",
                "zh-Hant": "繁體中文"
            }
            
            target_display = target_lang_map.get(target_lang, target_lang)
            prompt = f"将以下文本翻译为{target_display}，注意只需要输出翻译后的结果，不要额外解释：\n\n{text}"
            
            # 构建模型路径
            if not os.path.isabs(model_dir):
                base_dir = os.path.dirname(__file__)
                model_dir = os.path.join(base_dir, "..", model_dir)
                model_dir = os.path.normpath(model_dir)
            
            # 如果没有指定当前模型，尝试查找第一个 .gguf 文件
            if not current_model:
                if os.path.exists(model_dir):
                    for file in os.listdir(model_dir):
                        if file.endswith('.gguf'):
                            current_model = file
                            break
            
            if not current_model:
                return {
                    "success": False,
                    "error": f"模型文件夹中没有找到 .gguf 文件: {model_dir}"
                }
            
            model_path = os.path.join(model_dir, current_model)
            
            # 检查模型文件是否存在
            if not os.path.exists(model_path):
                return {
                    "success": False,
                    "error": f"模型文件不存在: {model_path}。请下载合适的GGUF格式翻译模型"
                }
            
            # 检查模型文件是否存在
            if not os.path.exists(model_path):
                return {
                    "success": False,
                    "error": f"模型文件不存在: {model_path}。请下载合适的GGUF格式翻译模型"
                }
            
            # 如果模型实例不存在或推理模式已更改，则创建新实例
            if self.llm_instance is None or hasattr(self, '_need_recreate') and self._need_recreate:
                # CPU推理参数设置 (仅Windows)
                # 如果已有实例，先清理旧实例
                if self.llm_instance is not None:
                    logger.info("清理旧模型实例")
                    try:
                        # 尝试清理当前实例
                        del self.llm_instance
                    except:
                        pass
                    self.llm_instance = None
                
                # 创建模型实例
                logger.info(f"创建CPU模型实例，模型路径: {model_path}，线程数: {threads}")
                self.llm_instance = Llama(**{
                    "model_path": model_path,
                    "n_ctx": context_length,  # 从配置文件获取上下文长度
                    "n_gpu_layers": 0,  # 禁用GPU，仅使用CPU
                    "n_threads": threads,  # 从配置文件获取线程数
                    "verbose": False  # 关闭详细输出
                })
                if hasattr(self, '_need_recreate'):
                    delattr(self, '_need_recreate')
            
            # 计算token数量，如果超过上下文窗口则分段翻译
            # 估算：中文约1.5字符/token，英文约4字符/token
            estimated_tokens = len(text) // 3  # 保守估计
            
            if estimated_tokens > context_length * 0.8:  # 留20%余量
                logger.info(f"文本过长（估计{estimated_tokens} tokens），将分段翻译")
                return await self._translate_in_chunks(text, target_display, context_length, max_tokens, temperature)
            
            # 使用现有模型实例执行翻译（使用流式输出）
            logger.info(f"开始CPU翻译，文本长度: {len(text)}, 预览: {text[:50]}...")
            translated_text = ""
            
            # 使用流式生成
            output = self.llm_instance(
                prompt,
                max_tokens=max_tokens,  # 从配置文件获取最大token数
                temperature=temperature,  # 从配置文件获取温度
                stop=["###"],  # 停止词 (移除 \n\n 以防截断多段落文本)
                stream=True  # 启用流式输出
            )
            
            # 收集流式输出
            for chunk in output:
                if 'choices' in chunk and len(chunk['choices']) > 0:
                    delta = chunk['choices'][0].get('text', '')
                    if delta:
                        translated_text += delta
            
            return {
                "success": True,
                "translated_text": translated_text,
                "source_lang": source_lang,
                "target_lang": target_lang
            }
        except ImportError:
            logger.error("llama-cpp-python库未安装，请运行: pip install llama-cpp-python")
            return {
                "success": False,
                "error": "llama-cpp-python库未安装，请运行: pip install llama-cpp-python"
            }
        except Exception as e:
            logger.error(f"llama-cpp翻译出错: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _translate_in_chunks(self, text: str, target_display: str, context_length: int, max_tokens: int, temperature: float) -> Dict[str, str]:
        """
        分段翻译长文本
        """
        try:
            from llama_cpp import Llama
            import os
            
            # 按段落分段（按换行符和句号分割）
            paragraphs = []
            current_chunk = ""
            
            # 按行分割，保留段落结构
            lines = text.split('\n')
            for line in lines:
                # 估算当前chunk的token数
                estimated_chunk_tokens = len(current_chunk + line) // 3
                
                if estimated_chunk_tokens > context_length * 0.6:  # 留40%余量给prompt
                    if current_chunk.strip():
                        paragraphs.append(current_chunk.strip())
                    current_chunk = line + "\n"
                else:
                    current_chunk += line + "\n"
            
            # 添加最后一个chunk
            if current_chunk.strip():
                paragraphs.append(current_chunk.strip())
            
            logger.info(f"文本分为{len(paragraphs)}段进行翻译")
            
            # 确保模型实例存在
            if self.llm_instance is None:
                logger.error("模型实例不存在，无法进行分段翻译")
                return {
                    "success": False,
                    "error": "模型实例不存在，无法进行分段翻译"
                }
            
            # 翻译每一段
            translated_paragraphs = []
            for i, paragraph in enumerate(paragraphs):
                if not paragraph.strip():
                    translated_paragraphs.append("")
                    continue
                
                prompt = f"将以下文本翻译为{target_display}，注意只需要输出翻译后的结果，不要额外解释：\n\n{paragraph}"
                
                try:
                    output = self.llm_instance(
                        prompt,
                        max_tokens=max_tokens,
                        temperature=temperature,
                        stop=["###"],
                        stream=True
                    )
                    
                    translated_text = ""
                    for chunk in output:
                        if 'choices' in chunk and len(chunk['choices']) > 0:
                            delta = chunk['choices'][0].get('text', '')
                            if delta:
                                translated_text += delta
                    
                    translated_paragraphs.append(translated_text)
                    logger.info(f"第{i+1}/{len(paragraphs)}段翻译完成")
                except Exception as e:
                    logger.error(f"翻译第{i+1}段时出错: {str(e)}")
                    translated_paragraphs.append(paragraph)  # 翻译失败时保留原文
            
            # 合并翻译结果
            final_text = '\n'.join(translated_paragraphs)
            
            return {
                "success": True,
                "translated_text": final_text,
                "source_lang": "auto",
                "target_lang": "zh"
            }
        except Exception as e:
            logger.error(f"分段翻译失败: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": f"分段翻译失败: {str(e)}"
            }

    async def translate_with_baidu(self, text: str, source_lang: str = "auto", target_lang: str = "zh") -> Dict[str, str]:
        """
        使用百度翻译API进行翻译
        """
        try:
            import requests
            import random
            from hashlib import md5
            import json
            import os
            
            # 从配置文件加载参数
            config_path = os.path.join(os.path.dirname(__file__), "../config.json")
            config = {}
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
            
            appid = config.get("baidu_appid", "")
            appkey = config.get("baidu_appkey", "")
            
            if not appid or not appkey:
                return {
                    "success": False,
                    "error": "百度翻译API配置不完整，请在设置中配置App ID和App Key"
                }
            
            # 百度翻译API语言代码映射
            lang_map = {
                "zh": "zh",
                "en": "en",
                "ja": "jp",
                "ko": "kor",
                "fr": "fra",
                "de": "de",
                "es": "spa",
                "ru": "ru",
                "ar": "ara"
            }
            
            # 转换目标语言代码
            to_lang = lang_map.get(target_lang, "zh")
            
            # 处理源语言
            if source_lang == "auto":
                from_lang = "auto"
            else:
                from_lang = lang_map.get(source_lang, "auto")
            
            # 百度翻译API端点
            endpoint = 'http://api.fanyi.baidu.com'
            path = '/api/trans/vip/translate'
            url = endpoint + path
            
            # 检查文本长度，如果太长则分段翻译
            # 百度API限制：单次请求的URL长度不能超过2048字符
            # 估算：每个中文字符约2-3字节，英文约1字节
            # 为了安全，每段不超过1500字符
            max_chars_per_request = 1500
            
            if len(text) > max_chars_per_request:
                logger.info(f"文本过长（{len(text)}字符），将分段翻译")
                return await self._translate_baidu_in_chunks(text, appid, appkey, from_lang, to_lang, url, max_chars_per_request)
            
            # 生成salt和sign
            def make_md5(s, encoding='utf-8'):
                return md5(s.encode(encoding)).hexdigest()
            
            salt = random.randint(32768, 65536)
            sign = make_md5(appid + text + str(salt) + appkey)
            
            # 构建请求
            headers = {'Content-Type': 'application/x-www-form-urlencoded'}
            payload = {
                'appid': appid,
                'q': text,
                'from': from_lang,
                'to': to_lang,
                'salt': salt,
                'sign': sign
            }
            
            # 发送请求
            logger.info(f"发送百度翻译请求，文本长度: {len(text)}")
            response = requests.post(url, params=payload, headers=headers, timeout=10)
            logger.info(f"百度翻译API响应状态码: {response.status_code}")
            
            # 检查响应状态
            if response.status_code != 200:
                logger.error(f"百度翻译API返回错误状态码: {response.status_code}")
                return {
                    "success": False,
                    "error": f"百度翻译API返回错误状态码: {response.status_code}"
                }
            
            # 检查响应内容
            response_text = response.text.strip()
            logger.info(f"百度翻译API响应内容长度: {len(response_text)}")
            
            if not response_text:
                logger.error("百度翻译API返回空响应")
                return {
                    "success": False,
                    "error": "百度翻译API返回空响应"
                }
            
            # 记录响应内容的前500个字符用于调试
            logger.info(f"百度翻译API响应内容预览: {response_text[:500]}")
            
            # 尝试解析JSON
            try:
                result = json.loads(response_text)
            except json.JSONDecodeError as e:
                logger.error(f"百度翻译API返回非JSON格式: {response_text[:200]}")
                logger.error(f"JSON解析错误详情: {str(e)}")
                return {
                    "success": False,
                    "error": f"百度翻译API返回非JSON格式: {str(e)}"
                }
            
            # 检查错误
            if 'error_code' in result:
                error_msg = result.get('error_msg', f"错误代码: {result.get('error_code')}")
                logger.error(f"百度翻译API错误: {error_msg}")
                return {
                    "success": False,
                    "error": f"百度翻译API错误: {error_msg}"
                }
            
            # 提取翻译结果
            if 'trans_result' in result and len(result['trans_result']) > 0:
                translated_text = result['trans_result'][0].get('dst', '')
                detected_lang = result.get('from', source_lang)
                
                return {
                    "success": True,
                    "translated_text": translated_text,
                    "source_lang": detected_lang,
                    "target_lang": target_lang
                }
            else:
                return {
                    "success": False,
                    "error": "百度翻译API返回结果格式错误"
                }
                
        except ImportError:
            logger.error("requests库未安装，请运行: pip install requests")
            return {
                "success": False,
                "error": "requests库未安装，请运行: pip install requests"
            }
        except Exception as e:
            logger.error(f"百度翻译出错: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _translate_baidu_in_chunks(self, text: str, appid: str, appkey: str, from_lang: str, to_lang: str, url: str, max_chars: int) -> Dict[str, str]:
        """
        分段翻译长文本（百度API）
        """
        try:
            import requests
            import random
            from hashlib import md5
            import json
            
            # 按段落分段（按换行符分割）
            paragraphs = []
            current_chunk = ""
            
            # 按行分割，保留段落结构
            lines = text.split('\n')
            for line in lines:
                # 估算当前chunk的字符数
                estimated_chunk_chars = len(current_chunk + line)
                
                if estimated_chunk_chars > max_chars * 0.8:  # 留20%余量给其他参数
                    if current_chunk.strip():
                        paragraphs.append(current_chunk.strip())
                    current_chunk = line + "\n"
                else:
                    current_chunk += line + "\n"
            
            # 添加最后一个chunk
            if current_chunk.strip():
                paragraphs.append(current_chunk.strip())
            
            logger.info(f"文本分为{len(paragraphs)}段进行翻译")
            
            # 翻译每一段
            translated_paragraphs = []
            def make_md5(s, encoding='utf-8'):
                return md5(s.encode(encoding)).hexdigest()
            
            for i, paragraph in enumerate(paragraphs):
                if not paragraph.strip():
                    translated_paragraphs.append("")
                    continue
                
                try:
                    # 生成salt和sign
                    salt = random.randint(32768, 65536)
                    sign = make_md5(appid + paragraph + str(salt) + appkey)
                    
                    # 构建请求
                    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
                    payload = {
                        'appid': appid,
                        'q': paragraph,
                        'from': from_lang,
                        'to': to_lang,
                        'salt': salt,
                        'sign': sign
                    }
                    
                    # 发送请求
                    logger.info(f"发送百度翻译请求（第{i+1}/{len(paragraphs)}段），文本长度: {len(paragraph)}")
                    response = requests.post(url, params=payload, headers=headers, timeout=10)
                    
                    # 检查响应状态
                    if response.status_code != 200:
                        logger.error(f"翻译第{i+1}段时出错，状态码: {response.status_code}")
                        translated_paragraphs.append(paragraph)  # 翻译失败时保留原文
                        continue
                    
                    # 解析响应
                    response_text = response.text.strip()
                    result = json.loads(response_text)
                    
                    # 检查错误
                    if 'error_code' in result:
                        logger.error(f"翻译第{i+1}段时出错: {result.get('error_msg')}")
                        translated_paragraphs.append(paragraph)  # 翻译失败时保留原文
                        continue
                    
                    # 提取翻译结果
                    if 'trans_result' in result and len(result['trans_result']) > 0:
                        translated_text = result['trans_result'][0].get('dst', '')
                        translated_paragraphs.append(translated_text)
                        logger.info(f"第{i+1}/{len(paragraphs)}段翻译完成")
                    else:
                        logger.error(f"翻译第{i+1}段时出错: 返回格式错误")
                        translated_paragraphs.append(paragraph)  # 翻译失败时保留原文
                        
                except Exception as e:
                    logger.error(f"翻译第{i+1}段时出错: {str(e)}")
                    translated_paragraphs.append(paragraph)  # 翻译失败时保留原文
            
            # 合并翻译结果
            final_text = '\n'.join(translated_paragraphs)
            
            return {
                "success": True,
                "translated_text": final_text,
                "source_lang": from_lang,
                "target_lang": to_lang
            }
        except Exception as e:
            logger.error(f"百度分段翻译失败: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": f"百度分段翻译失败: {str(e)}"
            }
    
    def set_inference_mode(self, mode: str):
        """
        设置推理模式 (仅CPU)
        """
        if mode in ["cpu"]:
            if self.inference_mode != mode:
                self.inference_mode = mode
                # 重置LLM实例以应用新模式
                self.llm_instance = None
                # 标记需要重新创建实例
                self._need_recreate = True
                logger.info(f"推理模式已设置为: {mode}")
            else:
                logger.info(f"推理模式已经是: {mode}")
            return True
        else:
            logger.error(f"无效的推理模式: {mode}，仅支持cpu模式")
            return False
    
    def get_inference_mode(self):
        """
        获取当前推理模式
        """
        return self.inference_mode
    
    def get_gpu_utilization(self):
        """
        获取GPU利用率信息（不适用，仅CPU模式）
        """
        return {
            "gpu_layers_used": 0,
            "is_using_gpu": False,
            "using_cpu": True
        }

    def get_config(self):
        """
        获取配置信息
        优先级：resources/config.json > 用户配置目录 > 默认配置
        """
        import json
        import os
        from pathlib import Path
        
        # 优先查找 resources/config.json（打包后的位置或开发模式的位置）
        # backend 目录在 resources/backend/，所以 ../config.json 就是 resources/config.json
        resources_config_path = os.path.join(os.path.dirname(__file__), "../config.json")
        if os.path.exists(resources_config_path):
            try:
                with open(resources_config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    # 兼容旧的配置格式：如果有 model_path，转换为 model_dir 和 current_model
                    if "model_path" in config and "model_dir" not in config:
                        old_model_path = config["model_path"]
                        # 提取目录和文件名
                        model_dir = os.path.dirname(old_model_path)
                        model_name = os.path.basename(old_model_path)
                        # 如果是相对路径，转换为相对于 resources 的路径
                        if not os.path.isabs(model_dir):
                            base_dir = os.path.dirname(__file__)
                            model_dir = os.path.join(base_dir, "..", model_dir)
                            model_dir = os.path.normpath(model_dir)
                        config["model_dir"] = model_dir
                        config["current_model"] = model_name
                        # 删除旧的 model_path
                        del config["model_path"]
                        # 保存更新后的配置
                        self.update_config(config)
                    return config
            except Exception as e:
                logger.warning(f"读取 resources/config.json 失败: {str(e)}")
        
        # 如果 resources/config.json 不存在，尝试使用用户配置目录（如果 appdirs 可用）
        try:
            import appdirs
            data_dir = appdirs.user_data_dir("TranslatorApp", "Translator")
            user_config_path = Path(data_dir) / "config.json"
            
            if user_config_path.exists():
                with open(user_config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except ImportError:
            # appdirs 不可用，跳过用户配置目录
            pass
        except Exception as e:
            logger.warning(f"读取用户配置失败: {str(e)}")
        
        # 如果都没有找到，返回默认配置
        return {
            "model_dir": "./models",
            "current_model": "",
            "context_length": 2048,
            "threads": 4,
            "max_tokens": 512,
            "temperature": 0.1,
            "api_base_url": "http://127.0.0.1:8000",
            "timeout": 5000,
            "auto_copy": False,
            "dark_mode": False,
            "theme_color": "#6366f1"
        }

    def update_config(self, new_config):
        """
        更新配置信息
        优先保存到 resources/config.json（打包后的位置或开发模式的位置）
        """
        import json
        import os
        from pathlib import Path
        
        # 优先保存到 resources/config.json（与读取保持一致）
        config_path = os.path.join(os.path.dirname(__file__), "../config.json")
        try:
            # 确保目录存在
            config_dir = os.path.dirname(config_path)
            if config_dir and not os.path.exists(config_dir):
                os.makedirs(config_dir, exist_ok=True)
            
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(new_config, f, indent=2, ensure_ascii=False)
            return {"success": True, "message": "配置已保存到 resources/config.json"}
        except Exception as e:
            logger.error(f"保存配置到 resources/config.json 失败: {str(e)}")
            # 如果保存失败，尝试保存到用户配置目录
            try:
                import appdirs
                data_dir = appdirs.user_data_dir("TranslatorApp", "Translator")
                user_config_path = Path(data_dir) / "config.json"
                user_config_path.parent.mkdir(parents=True, exist_ok=True)
                
                with open(user_config_path, 'w', encoding='utf-8') as f:
                    json.dump(new_config, f, indent=2, ensure_ascii=False)
                return {"success": True, "message": "配置已保存到用户配置目录"}
            except ImportError:
                # appdirs 不可用
                pass
            except Exception as e2:
                logger.error(f"保存配置到用户目录也失败: {str(e2)}")
            
            return {"success": False, "error": str(e)}
    
    def get_models_list(self):
        """
        获取模型文件夹中的模型列表
        返回所有 .gguf 文件
        """
        import os
        from pathlib import Path
        
        try:
            config = self.get_config()
            model_dir = config.get("model_dir", "./models")
            
            # 如果路径是相对路径，转换为绝对路径
            if not os.path.isabs(model_dir):
                # 相对于 backend 目录
                base_dir = os.path.dirname(__file__)
                model_dir = os.path.join(base_dir, "..", model_dir)
                model_dir = os.path.normpath(model_dir)
            
            if not os.path.exists(model_dir):
                return {
                    "success": False,
                    "error": f"模型文件夹不存在: {model_dir}",
                    "models": []
                }
            
            # 查找所有 .gguf 文件
            models = []
            for file in os.listdir(model_dir):
                if file.endswith('.gguf'):
                    file_path = os.path.join(model_dir, file)
                    file_size = os.path.getsize(file_path)
                    models.append({
                        "name": file,
                        "path": file_path,
                        "size": file_size,
                        "size_mb": round(file_size / (1024 * 1024), 2)
                    })
            
            # 按文件名排序
            models.sort(key=lambda x: x["name"])
            
            return {
                "success": True,
                "models": models,
                "model_dir": model_dir
            }
        except Exception as e:
            logger.error(f"获取模型列表失败: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "models": []
            }
    
    def switch_model(self, model_name):
        """
        切换模型
        如果模型已加载，需要重新加载
        """
        import os
        
        try:
            config = self.get_config()
            model_dir = config.get("model_dir", "./models")
            
            # 如果路径是相对路径，转换为绝对路径
            if not os.path.isabs(model_dir):
                base_dir = os.path.dirname(__file__)
                model_dir = os.path.join(base_dir, "..", model_dir)
                model_dir = os.path.normpath(model_dir)
            
            model_path = os.path.join(model_dir, model_name)
            
            if not os.path.exists(model_path):
                return {
                    "success": False,
                    "error": f"模型文件不存在: {model_path}"
                }
            
            # 更新配置中的当前模型
            config["current_model"] = model_name
            self.update_config(config)
            
            # 标记需要重新创建模型实例
            if self.llm_instance is not None:
                try:
                    del self.llm_instance
                except:
                    pass
                self.llm_instance = None
                self._need_recreate = True
            
            logger.info(f"已切换到模型: {model_name}")
            
            return {
                "success": True,
                "message": f"已切换到模型: {model_name}",
                "model_path": model_path
            }
        except Exception as e:
            logger.error(f"切换模型失败: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    async def translate_pdf_stream(self, pdf_path: str, source_lang: str, target_lang: str, provider: str, save_path: str, smart_layout: bool = True):
        """
        流式翻译PDF文件(保持排版)，产生进度事件
        """
        import os
        import json
        import fitz  # pymupdf
        import platform
        
        try:
            # 1. 打开PDF文件
            doc = fitz.open(pdf_path)
            total_pages = len(doc)
            
            yield json.dumps({
                "type": "progress", 
                "stage": "analyzing", 
                "total_pages": total_pages,
                "message": f"正在分析PDF排版，共 {total_pages} 页..."
            }) + "\n"
            
            # 2. 遍历每一页进行处理
            for page_num in range(total_pages):
                page = doc[page_num]
                
                # 获取页面信息（字典模式，包含字体信息）
                # 'dict' returns: {width, height, blocks: [{type, bbox, lines: [{spans: [{size, font, color, text, bbox...}]}]}]}
                page_dict = page.get_text("dict")
                blocks = page_dict.get("blocks", [])
                
                # 过滤出文本块
                text_blocks = [b for b in blocks if b.get("type", 0) == 0]
                
                # 按垂直(y0)主要排序，水平(x0)次要排序，确保阅读顺序
                text_blocks.sort(key=lambda b: (b["bbox"][1], b["bbox"][0]))
                
                total_blocks = len(text_blocks)
                
                # 发送页面开始事件
                msg = f"正在翻译第 {page_num + 1}/{total_pages} 页..."
                logger.info(msg)
                yield json.dumps({
                    "type": "progress", 
                    "stage": "translating", 
                    "current_page": page_num + 1, 
                    "total_pages": total_pages,
                    "total_segments": total_blocks,
                    "current_segment": 0,
                    "message": f"正在翻译第 {page_num + 1}/{total_pages} 页..."
                }) + "\n"
                
                # 确定中文字体路径
                font_path = None
                system = platform.system()
                if system == "Windows":
                    font_paths = ["C:\\Windows\\Fonts\\msyh.ttc", "C:\\Windows\\Fonts\\simhei.ttf"]
                    for p in font_paths:
                        if os.path.exists(p):
                            font_path = p
                            break
                elif system == "Darwin":
                    font_path = "/System/Library/Fonts/PingFang.ttc"
                else: # Linux
                    font_path = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
                
                # 如果找不到系统字体，尝试使用内置字体（可能不支持中文但能运行）
                if not font_path or not os.path.exists(font_path):
                     fontname = "china-ss" # pymupdf内置简体中文字体别名 (宋体)
                     fontfile = None
                else:
                     fontname = "custom-font"
                     fontfile = font_path

                # 逐个块处理
                for i, block in enumerate(text_blocks):
                    bbox = block["bbox"]
                    x0, y0, x1, y1 = bbox
                    
                    # 提取文本并分析各行字体
                    block_text = ""
                    font_sizes = []
                    
                    for line in block.get("lines", []):
                        line_text = ""
                        for span in line.get("spans", []):
                            line_text += span.get("text", "")
                            if smart_layout:
                                font_sizes.append(span.get("size", 10))
                        block_text += line_text + "\n"
                        
                    text = block_text.strip()
                    if not text:
                        continue
                     
                    # 发送当前块开始翻译事件
                    msg = f"正在翻译第 {page_num + 1}/{total_pages} 页 (块 {i+1}/{total_blocks})..."
                    if i % 5 == 0:
                        logger.info(msg)
                    
                    yield json.dumps({
                        "type": "progress", 
                        "stage": "translating", 
                        "current_page": page_num + 1, 
                        "total_pages": total_pages,
                        "current_segment": i + 1,
                        "total_segments": total_blocks,
                        "message": f"正在翻译第 {page_num + 1}/{total_pages} 页 (块 {i+1}/{total_blocks})..."
                    }) + "\n"
                        
                    # 翻译文本块
                    try:
                        result = await self.translate(text, source_lang, target_lang, provider)
                        if result["success"]:
                            translated_text = result["translated_text"]
                            
                            # 替换文本
                            # 1. 删除原内容
                            rect = fitz.Rect(x0, y0, x1, y1)
                            page.add_redact_annot(rect, fill=(1, 1, 1)) # 使用白色填充删除区域
                            page.apply_redactions()
                            
                            # 2. 写入新文本
                            # 需要注册字体
                            if fontfile:
                                page.insert_font(fontname=fontname, fontfile=fontfile)
                            
                            # 确定目标字号
                            target_fontsize = 10 # 默认
                            if smart_layout and font_sizes:
                                # 取出现次数最多的字号作为基准
                                try:
                                    target_fontsize = max(set(font_sizes), key=font_sizes.count)
                                    # 翻译为中文通常更紧凑，稍微减小一点点以防溢出，但如果是标题(>14)则保留
                                    if target_fontsize < 14:
                                        target_fontsize = max(6, target_fontsize - 1)
                                except:
                                    pass
                            
                            # 尝试多次插入，调节字体大小
                            inserted = False
                            # 尝试从目标字号开始向下尝试
                            start_size = int(target_fontsize) if smart_layout else 10
                            # 确保至少尝试到 6
                            sizes_to_try = list(range(start_size, 5, -1))
                            if not sizes_to_try: # if start_size is small
                                sizes_to_try = [start_size]
                            
                            for fontsize in sizes_to_try:
                                ret = page.insert_textbox(rect, translated_text, fontname=fontname, fontsize=fontsize, align=0, color=(0, 0, 0))
                                if ret >= 0:
                                    inserted = True
                                    break
                            
                            if not inserted:
                                logger.warning(f"Page {page_num+1} Block {i} 文本过长无法完整放入框内: {translated_text[:20]}...")
                                # forcefully insert with smallest font
                                page.insert_textbox(rect, translated_text, fontname=fontname, fontsize=5, align=0, color=(0, 0, 0))
                            
                        else:
                            logger.error(f"Page {page_num+1} Block {i} translation failed: {result.get('error')}")
                    except Exception as e:
                        logger.error(f"Page {page_num+1} Block {i} error: {e}")
            
            # 3. 保存新文件
            yield json.dumps({
                "type": "progress", 
                "stage": "generating", 
                "message": "正在保存PDF文件..."
            }) + "\n"
            
            # 使用临时文件保存以支持覆盖原文件（非增量保存需要）
            temp_save_path = f"{save_path}.tmp"
            try:
                # 使用垃圾回收和压缩保存
                doc.save(temp_save_path, garbage=4, deflate=True)
                doc.close()
                
                # 移动/覆盖文件
                if os.path.exists(save_path):
                     os.remove(save_path)
                os.rename(temp_save_path, save_path)
                
            except Exception as e:
                # 如果出错，尝试清理临时文件
                if os.path.exists(temp_save_path):
                    try:
                        os.remove(temp_save_path)
                    except:
                        pass
                raise e # 重新抛出异常给外层处理
            
            yield json.dumps({
                "type": "complete", 
                "success": True, 
                "save_path": save_path,
                "message": "翻译完成"
            }) + "\n"
            
        except ImportError:
             logger.error("pymupdf库未安装")
             yield json.dumps({
                "type": "error", 
                "error": "pymupdf库未安装，请运行 pip install pymupdf"
            }) + "\n"
        except Exception as e:
            logger.error(f"PDF流式翻译(排版保留)失败: {str(e)}", exc_info=True)
            yield json.dumps({
                "type": "error", 
                "error": str(e),
                "message": f"处理出错: {str(e)}"
            }) + "\n"

    # 以下旧方法保留作为备用或删除
    # extract_and_segment_pdf 和 create_pdf_from_text 不再被翻译流程主要调用


# 全局翻译器实例
translator = Translator()

async def init_translator():
    """初始化翻译器"""
    await translator.init()

async def cleanup_translator():
    """清理翻译器"""
    await translator.cleanup()