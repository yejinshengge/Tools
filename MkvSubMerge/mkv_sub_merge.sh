#!/bin/sh

# 定义视频和字幕目录
VIDEO_DIR="/storage/videos"    # 视频文件目录
SUB_DIR="/storage/subs"        # 字幕文件目录
OUTPUT_DIR="/storage/output"   # 输出目录

# 支持的文件扩展名
VIDEO_EXTENSIONS="mp4|mkv|avi|mov|wmv|flv|webm|m4v|mpg|mpeg"  # 视频文件扩展名
SUBTITLE_EXTENSIONS="srt|ass|ssa|vtt"                         # 字幕文件扩展名

# 创建输出目录
mkdir -p "$OUTPUT_DIR"

# 遍历视频目录中的文件
for video_file in "$VIDEO_DIR"/*; do
    # 跳过目录
    [ ! -f "$video_file" ] && continue
    
    # 只处理视频文件（使用 case 语句匹配扩展名）
    case "$video_file" in
        *.mp4|*.mkv|*.avi|*.mov|*.wmv|*.flv|*.webm|*.m4v|*.mpg|*.mpeg)
            # 是视频文件，继续处理
            ;;
        *)
            # 不是视频文件，跳过
            continue
            ;;
    esac
    
    # 提取文件名（不含扩展名）
    base_name=$(basename "$video_file" | sed 's/\.[^.]*$//')
    
    # 初始化字幕文件选项字符串
    subtitle_options=""
    
    # 查找所有可能语言的字幕文件
    for sub_file in "$SUB_DIR"/"$base_name".*; do
        # 检查文件是否存在
        [ ! -f "$sub_file" ] && continue
        
        # 检查是否为字幕文件（使用 case 语句）
        case "$sub_file" in
            *.srt|*.ass|*.ssa|*.vtt)
                # 是字幕文件，继续处理
                ;;
            *)
                # 不是字幕文件，跳过
                continue
                ;;
        esac
        
        # 提取字幕语言代码（假设字幕文件扩展名格式为：基础名.语言代码.扩展名，如 movie.zh.srt）
        sub_filename=$(basename "$sub_file")
        
        # 统计文件名中的点的数量
        dot_count=$(echo "$sub_filename" | tr -cd '.' | wc -c)
        
        # 如果文件名有至少两个点（如 movie.zh.srt），提取倒数第二个部分作为语言代码
        if [ "$dot_count" -ge 2 ]; then
            lang_code=$(echo "$sub_filename" | rev | cut -d '.' -f2 | rev)
        else
            # 否则使用默认值
            lang_code="und"
        fi
        
        # 验证语言代码（应该是2-3个字符的字母代码）
        # 使用 case 语句检查格式
        case "$lang_code" in
            [a-zA-Z][a-zA-Z]|[a-zA-Z][a-zA-Z][a-zA-Z])
                # 2-3个字母，有效
                ;;
            *)
                # 无效，使用默认值
                lang_code="und"
                ;;
        esac
        
        # 为每个字幕文件构建mkvmerge选项（sh 不支持 printf %q，使用引号包裹）
        subtitle_options="$subtitle_options --language 0:$lang_code --track-name 0:$lang_code \"$sub_file\""
        echo "  找到字幕: $(basename "$sub_file") (语言: $lang_code)"
    done
    
    # 如果有字幕文件，则执行合并
    if [ -n "$subtitle_options" ]; then
        output_file="$OUTPUT_DIR/$base_name.mkv"
        
        echo "正在处理: $(basename "$video_file")"
        
        # 使用mkvmerge合并视频和字幕（使用 eval 来正确处理引号）
        eval "mkvmerge -o \"$output_file\" \"$video_file\" $subtitle_options"
        if [ $? -eq 0 ]; then
            echo "✓ 成功: $base_name.mkv"
        else
            echo "✗ 失败: $base_name (mkvmerge 错误)"
        fi
    else
        echo "⊘ 跳过: $base_name (未找到匹配的字幕文件)"
    fi
done

echo "批量处理完成！"