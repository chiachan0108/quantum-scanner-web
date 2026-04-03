elif "S." in strategy_choice:
                id_map = {}
                for sid in df1['代號'].astype(str) if not df1.empty else []: id_map.setdefault(sid, set()).add("A")
                for sid in df2['代號'].astype(str) if not df2.empty else []: id_map.setdefault(sid, set()).add("B")
                for sid in df_d['代號'].astype(str) if not df_d.empty else []: id_map.setdefault(sid, set()).add("D")
                for sid in df_e['代號'].astype(str) if not df_e.empty else []: id_map.setdefault(sid, set()).add("E")
                for sid in df_squat['代號'].astype(str) if not df_squat.empty else []: id_map.setdefault(sid, set()).add("F")
                for sid in df_g['代號'].astype(str) if not df_g.empty else []: id_map.setdefault(sid, set()).add("G")
                for sid in df_h['代號'].astype(str) if not df_h.empty else []: id_map.setdefault(sid, set()).add("H")
                for sid in df_j['代號'].astype(str) if not df_j.empty else []: id_map.setdefault(sid, set()).add("J")
                for sid in df_k['代號'].astype(str) if not df_k.empty else []: id_map.setdefault(sid, set()).add("K")
                
                # 後處理組合標籤
                for sid, tags in id_map.items(): 
                    if "A" in tags and "B" in tags: tags.add("C")
                    if "A" in tags and "H" in tags: tags.add("I")
                    # 🌟 新增：讓策略 S 也能正確識別並標註出 R 策略
                    if len(tags.intersection({"A", "B", "D", "E", "F", "G", "H", "J", "K"})) >= 3: tags.add("R")

                dfs_to_concat = [d for d in [df1, df2, df_d, df_e, df_squat, df_g, df_h, df_j, df_k] if not d.empty]
